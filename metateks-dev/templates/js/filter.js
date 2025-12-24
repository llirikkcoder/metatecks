const attrName = '{{ attr.slug|default_if_none:"" }}',
      absolutePath = '{{ absolute_path }}',
      disabledClass = '_disabled',
      isSelectedClass = 'btn--filtr--select',
      brandAttrName = '{{ BRAND_ATTR_SLUG }}',
      brandSlugs = {{ brand_slugs|safe }};

var _filter = {'brand': []},
    _offset = 0;
if (attrName) { _filter[attrName] = []; }


/* === вспомогательные методы === */

// работа с фильтром (объект _filter)

function addToFilter(attr, value, _sort = true) {
  _filter[attr].push(value);
  if (_sort) { _filter[attr].sort(); }
}

function removeFromFilter(attr, value, _sort = true) {
  _filter[attr].push(value);
  _filter[attr] = _filter[attr].filter(function(el) { return el != value; });
  if (_sort) { _filter[attr].sort(); }
}

function setFilterEmpty() {
  _filter['brand'] = [];
  if (attrName) { _filter[attrName] = []; }
}

function initFilter() {
  var brandSelector = `.js-filter-option.${isSelectedClass}[data-attr="${brandAttrName}"]`,
      attrSelector = `.js-filter-option.${isSelectedClass}[data-attr="${attrName}"]`;

  $(brandSelector).each(function() { addToFilter('brand', $(this).data('value'), false) });
  _filter['brand'].sort();

  if (attrName) {
    $(attrSelector).each(function() { addToFilter(attrName, $(this).data('value'), false) });
    _filter[attrName].sort();
  }
}


// работа с переменной _offset

function setOffset(offset) {
  _offset = offset;
}


// получение params-строки для запроса на бекенд

function getFilterParams() {
  var p = {};
  if (_filter['brand'].length > 1) { p['brand'] = _filter['brand'].join('_'); }
  if (attrName && _filter[attrName].length) { p[attrName] = _filter[attrName].join('_'); }
  if (_offset) { p['offset'] = _offset; }
  return jQuery.param(p);
}


/* === основной метод: запрос с фильтром на бекенд === */

function resetDisabled() {
  // $(`.${disabledClass}`).removeClass(disabledClass);
  $('body').find(`.${disabledClass}`).removeClass(disabledClass);
}

function loadProducts(pagination = false) {
  var title = $(document).attr('title');
      currentUrl = location.href.replace(location.hash, ''),
      url = path = absolutePath,
      brandIds = null, brandId = null, brandSlug = null,
      params = null, $container = null;

  // - получение slug у бренда и смена урла
  brandIds = _filter['brand']
  if (brandIds.length == 1) {
    brandId = brandIds[0];
    brandSlug = brandSlugs[brandId];
    url = path = `${path}${brandSlug}/`;
  }

  // - получение GET-параметров и смена урла
  params = getFilterParams();
  if (params) { url = `${path}?${params}`; }

  // - меняем урл страницы + добавляем в историю
  if (!pagination && url != currentUrl) {
    history.pushState({}, title, url);
  }

  // - получаем контейнер для товаров
  // (и вешаем класс _disabled, если надо)
  if (pagination) {
    $container = $('.js-products-list');
  }
  else {
    $container = $('.js-filter-products');
    $container.addClass(disabledClass);
  }

  // - выполняем запрос на бек
  $.ajax({
    url: path,
    data: params,
    cache: false,
    success: function(res) {
      // -- в случае пагинации - добавляем товары к предыдущим + обновляем кнопку
      if (pagination) {
        var $button = $('.js-load-more'),
            $buttonContainer = $('.js-load-more-container');

        $container.append(res['html']);
        if (res['has_more']) {
          $button.attr('data-offset', res['new_offset']);
          $button.data('offset', res['new_offset']);
        }
        else { $buttonContainer.remove(); }
      }
      // -- в ином случае - обновляем контейнер с товарами
      else {
        $container.html(res['html']);
        if ($('.slider-products').length) { initProductsSlider(); }
      }
      resetDisabled();
    },
    always: function() {
      resetDisabled();
    }
  });
}


/* === триггеры === */

// - при загрузке страницы (заполняем объект filter)

$(document).ready(initFilter);


// - при фильтрации товаров

$('body').on('click', '.js-filter-option', function(e){
  e.preventDefault();

  var $button = $(this),
      isSelected = !($button.hasClass(isSelectedClass)),
      attr = $button.data('attr'),
      value = $button.data('value');

  $button.toggleClass(isSelectedClass);
  if (isSelected) { addToFilter(attr, value); }
  else { removeFromFilter(attr, value); }
  setOffset(0);
  loadProducts();
})


// - при нажатии "показать еще"

$('body').on('click', '.js-load-more', function(e){
  e.preventDefault();

  var $button = $(this),
      offset = parseInt($(this).data('offset'));

  setOffset(offset);
  $button.addClass(disabledClass);
  loadProducts(pagination=true);
})


// - при нажатии "сбросить фильтр"

$('body').on('click', '.js-reset-filter', function(e){
  e.preventDefault();

  var $button = $(this),
      $filterButtons = $('.js-filter-option');

  $filterButtons.removeClass(isSelectedClass);
  setOffset(0);
  setFilterEmpty();
  $button.addClass(disabledClass);
  loadProducts();
})


// - повторная инициализация слайдера (скопировано из swiper-initiation.js)

function initProductsSlider() {
  var swiper = new Swiper(".slider-products", {

    // Количество слайдов для показа
    slidesPerView: 4,
    breakpoints: {
      120: {
        slidesPerView: 1,
      },
      576: {
        slidesPerView: 2,
      },
      768: {
        slidesPerView: 3,
      },
      1200: {
        slidesPerView: 4,
      },
    },

    // Отступ между слайдами
    spaceBetween: 20,
    // Количество пролистываемых слайдов
    slidesPerGroup: 1,

    // Отключение функционала
    // если слайдов меньше чем нужно
    watchOverflow: true,
    // Отключить предзагрузка картинок
    preloadImages: false,
    // Lazy Loading
    // (подгрузка картинок)
    lazy: {
      // Подгружать на старте
      // переключения слайда
      loadOnTransitionStart: false,
      // Подгрузить предыдущую
      // и следующую картинки
      loadPrevNext: false,
    },

    // Обновить свайпер
    // при изменении элементов слайдера
    observer: true,

    // Обновить свайпер
    // при изменении родительских
    // элементов слайдера
    observeParents: true,

    // Обновить свайпер
    // при изменении дочерних
    // элементов слайда
    observeSlideChildren: true,

    // Бесконечный слайдер
    loop: true,
    loopFillGroupWithBlank: true,

    // Управление клавиатурой
    keyboard: {
      // Включить\выключить
      enabled: true,
      // Включить\выключить
      // только когда слайдер
      // в пределах вьюпорта
      onlyInViewport: true,
      // Включить\выключить
      // управление клавишами
      // pageUp, pageDown
      pageUpDown: true,
    },

    // Автовысота
    autoHeight: false,

    //  === Навигация 
    // Буллеты, текущее положение, прогрессбар
    pagination: {
      el: '.swiper-pagination',
      clickable: true,
    },

    // Стрелки
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },
  });
}
