
// Отправка запросов на бекенд

// - обновление позиции в корзине
function updateItem(data, itemType, $removedItem=null) {
  var url = urls[itemType];

  if ($removedItem) { $removedItem.addClass('_disabled'); }

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json',
    success: function(res){
      if ($removedItem) {
        $removedItem.slideUp(400, function(){
          var itemsCount = $('.js-cart-item:visible').length;
          // если айтемов не осталось, перезагружаем страницу
          if (!itemsCount) {
            document.getElementById('selectAll').checked = false;
            window.location.hash = '#header';
            window.location.reload();
          }
        });
      }
    },
    error: function(){
      if ($removedItem) { $removedItem.removeClass('_disabled'); }
    }
  });
}

// - массовое отключение/включение позиций
function groupToggle(isEnabled) {
  var url = urls.groupToggle,
      data = {'is_enabled': isEnabled};

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json',
  });
}

// - полная очистка корзины
function clearCart() {
  var $cartContainer = $('#js-cart-container');
      url = urls.clearCart;

  $cartContainer.addClass('_disabled');

  $.ajax({
    url: url,
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    success: function(res){
      var next = res['redirect_url'];
      if (next) { window.location = next; }
      else {
        window.location.hash = '#header';
        window.location.reload();
      }
    },
    complete: function(){
      $cartContainer.removeClass('_disabled');
    }
  });
}


// Выбор товаров в корзине
document.addEventListener('DOMContentLoaded', () => {
  const selectAllCheckbox = document.getElementById('selectAll');
  const itemCheckboxes = document.querySelectorAll('.item-checkbox');

  if (selectAllCheckbox && itemCheckboxes.length > 0) {
    // переключение глобального тоггла корзины
    selectAllCheckbox.addEventListener('change', () => {
      var isEnabled = selectAllCheckbox.checked;
      // - переключаем все тогглы у товаров
      itemCheckboxes.forEach(checkbox => {
        checkbox.checked = isEnabled;
      });
      // - отправляем данные на бек
      groupToggle(isEnabled);
    });

    // переключение тоггла у товара
    itemCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', () => {
        var isEnabled = checkbox.checked,
            $checkbox = $(checkbox),
            itemType = $checkbox.data('item-type'),
            productId = $checkbox.data('product-id'),
            extraId = $checkbox.data('extra-id');

        // - переключаем тогглы у дополнительных товаров
        if (itemType == 'product') {
          var extraQuery = `.item-checkbox[data-item-type="extra"][data-product-id="${productId}"]`,
              extraCheckboxes = document.querySelectorAll(extraQuery);
          extraCheckboxes.forEach(checkbox => {checkbox.checked = isEnabled;});
        }
        // - переключаем тоггл у родителя (если включаем доп.товар)
        else if (isEnabled) {
          var productQuery = `.item-checkbox[data-item-type="product"][data-product-id="${productId}"]`,
              productCheckboxes = document.querySelectorAll(productQuery);
          productCheckboxes.forEach(checkbox => {checkbox.checked = true;});
        }
        // - переключаем глобальный тоггл
        if (!isEnabled) {
          selectAllCheckbox.checked = false;
        } else {
          var allChecked = Array.from(itemCheckboxes).every(cb => cb.checked);
          selectAllCheckbox.checked = allChecked;
        }
        // - отправляем данные на бек
        var data = {'product_id': productId, 'extra_id': extraId, 'is_enabled': isEnabled};
        updateItem(data, itemType);
      });
    });
  }
});


// очистка корзины
document.addEventListener('DOMContentLoaded', () => {
  const cartClearButton = document.getElementById('js-clear-cart');
  cartClearButton.addEventListener('click', () => {
    if (confirm('Вы действительно хотите очистить корзину?')) {
      clearCart();
    }
  })
});


// количество в корзине + удаление позиции из корзины
document.addEventListener('DOMContentLoaded', () => {
  const productItems = document.querySelectorAll('.block--product--quantity');
  const totalPriceElement = document.getElementById('total-price');
  const totalQuantityElement = document.getElementById('total-quantity');
  const selectAllCheckbox = document.getElementById('selectAll');
  const itemCheckboxes = document.querySelectorAll('.item-checkbox');
  const removeItemButtons = document.querySelectorAll('.js-remove-item');

  function updateTotalPriceAndQuantity() {
    let total = 0;
    let totalQuantity = 0;
    itemCheckboxes.forEach((checkbox, index) => {
      if (checkbox.checked) {
        const costSpan = productItems[index].querySelector('.cart-product-cost');
        const quantitySpan = productItems[index].querySelector('.quantity');
        const cost = parseInt(costSpan.textContent.replace(/\D/g, ''), 10);
        const quantity = parseInt(quantitySpan.textContent, 10);
        total += cost;
        totalQuantity += quantity;
      }
    });
    totalPriceElement.textContent = total.toLocaleString('ru-RU') + ' ₽';
    totalQuantityElement.textContent = totalQuantity + ' шт.';
  }

  if (productItems.length > 0) {
    productItems.forEach(item => {
      const btnDecrease = item.querySelector('.btn-decrease');
      const btnIncrease = item.querySelector('.btn-increase');
      const quantitySpan = item.querySelector('.quantity');
      const priceSpan = item.querySelector('.cart-product-price');
      const costSpan = item.querySelector('.cart-product-cost');

      if (btnDecrease && btnIncrease && quantitySpan && priceSpan) {
        const pricePerItem = parseInt(priceSpan.textContent.replace(/\D/g, ''), 10);
        var $parent = $(item).parents('.js-cart-item'),
            itemType = $parent.data('item-type'),
            productId = $parent.data('product-id'),
            extraId = $parent.data('extra-id');
        var data = {'product_id': productId, 'extra_id': extraId};

        function updatePrice() {
          const quantity = parseInt(quantitySpan.textContent, 10);
          const totalPrice = pricePerItem * quantity;
          costSpan.textContent = totalPrice.toLocaleString('ru-RU') + ' ₽';
          updateTotalPriceAndQuantity();
        }

        function updateButtonState(quantity) {
          if (quantity <= 1) {
            btnDecrease.classList.add('disabled');
          } else {
            btnDecrease.classList.remove('disabled');
          }
        }

        btnDecrease.addEventListener('click', () => {
          let quantity = parseInt(quantitySpan.textContent, 10);
          if (quantity > 1) {
            quantity--;
            quantitySpan.textContent = quantity;
            updatePrice();
          }
          updateButtonState(quantity);
          data['quantity'] = quantity;
          updateItem(data, itemType);
        });

        btnIncrease.addEventListener('click', () => {
          let quantity = parseInt(quantitySpan.textContent, 10);
          quantity++;
          quantitySpan.textContent = quantity;
          updatePrice();
          updateButtonState(quantity);
          data['quantity'] = quantity;
          updateItem(data, itemType);
        });

        // Инициализация состояния кнопки при загрузке
        updateButtonState(parseInt(quantitySpan.textContent, 10));
      }
    });
  }

  selectAllCheckbox.addEventListener('change', () => {
    itemCheckboxes.forEach(checkbox => {
      checkbox.checked = selectAllCheckbox.checked;
    });
    updateTotalPriceAndQuantity();
  });

  itemCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', updateTotalPriceAndQuantity);
  });

  if (removeItemButtons.length > 0) {
    removeItemButtons.forEach(button => {
      button.addEventListener('click', () => {
        var $button = $(button),
            $parent = $button.parents('.js-cart-item'),
            itemType = $parent.data('item-type'),
            isProduct = (itemType == 'product'),
            productId = $parent.data('product-id'),
            extraId = $parent.data('extra-id'),
            $container = $parent,
            confirmMessage;

        confirmMessage = isProduct ? 'Удалить товар из корзины?' : 'Удалить дополнительный товар из корзины?';

        if (confirm(confirmMessage)) {
          var data = {'product_id': productId, 'extra_id': extraId, 'quantity': 0};
          if (isProduct) { $container = $container.parents('.js-cart-product-container'); }
          $container.find('.item-checkbox').each(function(index, checkbox){
            checkbox.checked = false;
          });
          updateTotalPriceAndQuantity();
          updateItem(data, itemType, $container);
        }
      });
    });
  };

  updateTotalPriceAndQuantity(); // Инициализация суммы и количества при загрузке страницы
});


// Для корзины:: Информация данных полей доставки предается в правый блок инфо
document.addEventListener('DOMContentLoaded', () => {
  const deliveryRadios = document.querySelectorAll('input[name="delivery"]');
  const deliveryInfo = document.getElementById('deliveryInfo');
  const trCompanyRadios = document.querySelectorAll('input[name="trcompany"]');
  const delivery1Radio = document.getElementById('delivery1');
  const delivery3Radio = document.getElementById('delivery3');
  const toggleBlocks = document.querySelectorAll('.toggle-block-address, .toggle-address');

  if (deliveryRadios.length > 0 && deliveryInfo) {
    deliveryRadios.forEach(radio => {
      radio.addEventListener('change', () => {
        updateDeliveryInfo();
      });
    });
  }

  if (trCompanyRadios.length > 0) {
    trCompanyRadios.forEach(radio => {
      radio.addEventListener('change', () => {
        if (delivery3Radio && !delivery3Radio.checked) {
          delivery3Radio.checked = true;
        }
        updateDeliveryInfo();
      });
    });
  }

  const toggleVisibility = () => {
    var displaySetting = delivery1Radio.checked ? 'none' : '';
    toggleBlocks.forEach(block => block.style.display = displaySetting);
  };

  function updateDeliveryInfo() {
    const selectedDelivery = document.querySelector('input[name="delivery"]:checked'),
          deliveryMethod = selectedDelivery.value,
          deliveryName = selectedDelivery.getAttribute('data-label');
    let selectedCompany = null,
        companyId = null,
        companyName = null;

    if (delivery3Radio.checked) {
      const selectedCompanyRadio = document.querySelector('input[name="trcompany"]:checked');
      if (selectedCompanyRadio) {
        companyId = selectedCompanyRadio.value,
        companyName = selectedCompanyRadio.getAttribute('data-label');
      }
    }

    var url = urls.updateData.deliveryMethod,
        data = {'method': deliveryMethod, 'company_id': companyId};

    $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify(data),
      dataType: 'json',
      contentType: 'application/json',
      success: function(){
        filledData.deliveryMethod = true;
        someData.deliveryMethod = deliveryMethod;
        // обновляем данные справа
        deliveryInfo.innerHTML = `<span>${deliveryName}${companyName ? `, ${companyName}` : ''}</span> <a href="#delivery" class="data_edit-btn dark--bgrnd"><span class="met-ico-edit"></span></a>`;
        // показываем/скрываем блоки с адресом доставки
        toggleVisibility();
      },
    });

  }
});


// Для корзины:: Информация данных полей формы Контактного лица предается в правый блок инфо
document.addEventListener('DOMContentLoaded', () => {
  var $form = $('#userForm'),
      userDataInfo = document.getElementById('userDataInfo');
  // const phoneInput = document.getElementById('phone');

  if ($form) {
    // // Инициализация маски ввода для телефона
    // if (phoneInput) {
    //   Inputmask("+7 (999) 999-99-99").mask(phoneInput);
    // }

    $form.on('submit', function(e) {
      e.preventDefault();
      var url = $form.attr('action'),
          data, form_data;

      data = getFormData($form);
      form_data = {'data': data};
      removeErrors($form);
      $form.addClass('_disabled');

      // const phonePattern = /^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$/;
      // if (!data.phone || !data.flagperson) {
      //   errorMessage.textContent = 'Пожалуйста, введите номер телефона и примите условия политики.';
      //   errorMessage.style.display = 'block';
      // } else if (!phonePattern.test(data.phone)) {
      //   errorMessage.textContent = 'Пожалуйста, введите корректный номер телефона в формате +7 (XXX) XXX-XX-XX.';
      //   errorMessage.style.display = 'block';
      // }

      $.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify(form_data),
        dataType: 'json',
        contentType: 'application/json',

        success: function(res){
          filledData.contactsData = true;
          // обновляем данные в правой колонке
          userDataInfo.innerHTML = `<span>${data.phone}, ${data.first_name} ${data.last_name}</span> <a href="#person" class="data_edit-btn dark--bgrnd"><span class="met-ico-edit"></span></a>`;
        },
        error: function(res){
          if (res.status == 400) {
            var response = res.responseJSON,
                errors = response['errors'];
            if (errors) { addErrors($form, errors); }
          }
        },
        complete: function(){
          $form.removeClass('_disabled');
        }
      });
    });
  }
});


// Для корзины:: Информация данных полей формы Адрес предается в правый блок инфо
document.addEventListener('DOMContentLoaded', () => {
  var $form = $('#addressForm'),
      addressInfo = document.getElementById('addressInfo');

  $form.on('submit', function(e) {
    e.preventDefault();
    var url = $form.attr('action'),
        data, form_data;

    data = getFormData($form);
    form_data = {'data': data};
    removeErrors($form);
    $form.addClass('_disabled');

    $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify(form_data),
      dataType: 'json',
      contentType: 'application/json',

      success: function(res){
        filledData.deliveryData = true;
        // обновляем данные в правой колонке
        addressInfo.innerHTML = `<span>${data.region}, ${data.city}, ${data.address}</span> <a href="#address" class="data_edit-btn dark--bgrnd"><span class="met-ico-edit"></span></a>`;
      },
      error: function(res){
        if (res.status == 400) {
          var response = res.responseJSON,
              errors = response['errors'];
          if (errors) { addErrors($form, errors); }
        }
      },
      complete: function(){
        $form.removeClass('_disabled');
      }
    });

  });
});


// Для корзины:: выбор способа оплаты
document.addEventListener('DOMContentLoaded', () => {
  const paymentRadios = document.querySelectorAll('input[name="payment"]'),
        onlinePayRadio = document.getElementById('online'),
        nonCashRadio = document.getElementById('non_cash');
  const $paymentForms = $('form.js-payment-form'),
        $cardFormInputs = $('#paymentCardForm input'),
        $cardFormSubmit = $('#paymentCardForm button[type="submit"]'),
        cardNumberInput = document.querySelector('#paymentCardForm input[name="card_number"]'),
        cardExpireInput = document.querySelector('#paymentCardForm input[name="card_expire"]'),
        $nonCashFormInputs = $('#paymentNoncashForm input'),
        organizationInput = document.querySelector('#paymentNoncashForm input[name="organization"]');
  const paymentInfo = document.getElementById('paymentInfo');
  let currentCardNumber, currentOrganizationName;

  function updatePaymentMethodText(paymentMethod) {
    var newStr = '';
    if (paymentMethod == 'online') {
      var number = cardNumberInput.value.slice(-4),
          expire = cardExpireInput.value;
      newStr = `Оплата онлайн, карта **${number} ${expire}`;
    }
    else if (paymentMethod == 'non_cash') {
      var organization = organizationInput.value;
      newStr = `Безналичная оплата, ${organization}`;
    }
    paymentMethodTexts[paymentMethod] = newStr;
  }

  function resetCardInputs(){
    $cardFormInputs.attr('disabled', false);
    $cardFormInputs.val('');
    $('input[name="card_number"]').mask('0000 0000 0000 0000', {clearIfNotMatch: true});
    $('input[name="card_expire"]').mask('00/00', {clearIfNotMatch: true});
    $('input[name="card_cvv"]').mask('000', {clearIfNotMatch: true});
    $cardFormSubmit.removeClass('js-disabled');
    $cardFormSubmit.find('.js-button-label').html('Сохранить');
  }

  // Обновление информации о способе оплаты в правом блоке
  const updatePaymentInfo = () => {
    var selectedOption = document.querySelector('input[name="payment"]:checked'),
        paymentMethod = selectedOption.value
        paymentText = paymentMethodTexts[paymentMethod];
    // if (paymentMethod == 'online' && currentCardNumber) { paymentText = `${paymentText}, карта сохранена`; }
    // else if (paymentMethod == 'non_cash' && currentOrganizationName) { paymentText = `${paymentText}, ${currentOrganizationName}`; }
    paymentInfo.innerHTML = `<span>${paymentText}</span> <a href="#payment" class="data_edit-btn dark--bgrnd"><span class="met-ico-edit"></span></a>`;
  };

  // Отправка запроса на смену радиобаттона
  const changePaymentMethod = () => {
    var selectedOption = document.querySelector('input[name="payment"]:checked'),
        paymentMethod = selectedOption.value;
    var url = urls.updateData.paymentMethod,
        data = {'method': paymentMethod};

    $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify(data),
      dataType: 'json',
      contentType: 'application/json',
      success: function(){
        filledData.paymentMethod = true;
        someData.paymentMethod = paymentMethod;
        // обновляем данные справа
        updatePaymentInfo();
      },
    });
  };

  // Обновление при изменении выбора радиокнопки
  if (paymentRadios.length > 0 && paymentInfo) {
    paymentRadios.forEach(radio => {
      radio.addEventListener('change', changePaymentMethod);
    });
  }

  // Изменяем радиобаттон при фокусировке в одну из форм
  const setPayActive = (button) => {
    if (button && !button.checked) {
      button.checked = true;
      changePaymentMethod();
    }
  };
  $cardFormInputs.on('focus', function(e) { setPayActive(onlinePayRadio); });
  $nonCashFormInputs.on('focus', function(e) { setPayActive(nonCashRadio); });

  // Отправка форм оплаты
  $paymentForms.on('submit', function(e) {
    e.preventDefault();
    var $form = $(this),
        isCardForm = $form.attr('id') == 'paymentCardForm',
        paymentMethod = isCardForm ? 'online' : 'non_cash';

    if (isCardForm && $cardFormSubmit.hasClass('js-disabled')) {
      resetCardInputs();
      $($cardFormInputs[0]).focus();
      return;
    }

    var url = $form.attr('action'),
        data, form_data;

    data = getFormData($form);
    form_data = {'data': data};
    removeErrors($form);
    $form.addClass('_disabled');

    $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify(form_data),
      dataType: 'json',
      contentType: 'application/json',
      success: function(res){
        if (isCardForm) { filledData.cardData = true; }
        else { filledData.cashlessData = true; }
        // обновляем текст в правой колонке
        updatePaymentMethodText(paymentMethod);
        updatePaymentInfo();
      },
      error: function(res){
        if (res.status == 400) {
          var response = res.responseJSON,
              errors = response['errors'];
          if (errors) { addErrors($form, errors); }
        }
      },
      complete: function(){
        $form.removeClass('_disabled');
      }
    });
  });
});


/* ====  Скрывающийся блок с информацией о заказе ======  */
document.addEventListener('DOMContentLoaded', () => {
  const fixedMobile = document.querySelector('.fixed-mobile');
  const fixedMobileTab = document.getElementById('fixedMobileTab');
  const checkboxRow = document.querySelector('.checkbox-row');

  if (fixedMobile && fixedMobileTab && checkboxRow) {
    // Изначальный текст на вкладке
    fixedMobileTab.textContent = 'Информация о заказе';

    fixedMobileTab.addEventListener('click', () => {
      fixedMobile.classList.toggle('show');
      if (fixedMobile.classList.contains('show')) {
        fixedMobileTab.textContent = 'Скрыть информацию';
      } else {
        fixedMobileTab.textContent = 'Информация о заказе';
      }
    });

    const observer = new MutationObserver(() => {
      if (fixedMobile.classList.contains('show')) {
        const fixedHeight = window.innerHeight - checkboxRow.getBoundingClientRect().top;
        if (fixedHeight < 0) {
          fixedMobile.classList.remove('show');
          fixedMobileTab.textContent = 'Информация о заказе';
        }
      }
    });

    observer.observe(checkboxRow, { childList: true, subtree: true });
  }
});


// === Оформление корзины ===

var checkoutSelector = '#js-checkout-button',
    authFormsSelector = '.js-cart-auth-form';


// -- Проверка: наличие товаров в корзине

function checkIsCartFilled() {
  var $enabledItems = $('.item-checkbox:checked');
  return Boolean($enabledItems.length);
}

// -- Проверка: заполненность данных

function checkLackingData() {
  var blocks = [];

  if (!filledData.deliveryMethod) { blocks.push('Способ доставки'); }
  else if (someData.deliveryMethod != 'pickup' && !filledData.deliveryData) {
    blocks.push('Адрес доставки');
  }
  if (!filledData.contactsData) { blocks.push('Контактные данные'); }
  if (!filledData.paymentMethod) { blocks.push('Метод оплаты'); }
  else if (someData.paymentMethod == 'online' && !filledData.cardData) {
    blocks.push('Данные карты для онлайн-оплаты');
  }
  else if (someData.paymentMethod == 'non_cash' && !filledData.cashlessData) {
    blocks.push('Данные для безналичной оплаты');
  }

  return blocks;
}


// -- Нажатие на кнопку "Оформить"

$(document).ready(function(){
  $(checkoutSelector).on('click', function(e){
    e.preventDefault();

    var $button = $(this),
        isCartFilled = checkIsCartFilled(),
        lackingData = checkLackingData(),
        errorMsg;

    // проверки и вывод алерта
    if (!isCartFilled) {
      errorMsg ='Ваша корзина пуста';
    }
    else if (lackingData.length) {
      errorMsg = 'Пожалуйста, заполните данные:',
      lackingData.forEach(function(block){
        errorMsg = `${errorMsg}<br/>– ${block}`
      })
    }
    if (errorMsg) {
      var $errorModal = $('#cart-errors'),
          $errorsContainer = $errorModal.find('#js-cart-errors');
      $errorsContainer.html(errorMsg);
      $errorModal.modal();
      return;
    }

    // если юзер не залогинен, выводим попап
    if (!isUserLogged) {
      $('#cart-login').modal();
      return;
    }

    // отправляем запрос на оформление
    makeCheckout($button);
  });
});


// -- Отправка форм логина/регистрации

$(document).ready(function(){
  $(authFormsSelector).on('submit', function(e) {
    e.preventDefault();

    var $form = $(this),
        $authForms = $(authFormsSelector),
        url = $form.attr('action'),
        form_data;

    form_data = getFormData($form);
    removeErrors($authForms);
    $authForms.addClass('_disabled');

    $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify(form_data),
      dataType: 'json',
      contentType: 'application/json',

      success: function(res){
        updateCsrfToken();
        isUserLogged = true;
        $.modal.close();
        $(checkoutSelector).click()
      },
      error: function(res){
        if (res.status == 400) {
          var response = res.responseJSON,
              errors = response['errors'];
          if (errors) { 
            if ($form) { addErrors($form, errors); }
            else { alert(`При отправке формы произошла ошибка: ${errors}`); }
          };
        }
      },
      complete: function(){
        $authForms.removeClass('_disabled');
      }
    });
  });
});


// -- Отправляем запрос на оформление корзины

function makeCheckout($button){
  var url = urls.checkout;

  $button.addClass('_disabled');

  $.ajax({
    url: url,
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    success: function(res){
      var next = res['redirect_url'];
      if (next) { window.location = next; }
      else { window.location = urls.successOrder; }
    },
    complete: function(){
      $button.removeClass('_disabled');
    }
  });
}
