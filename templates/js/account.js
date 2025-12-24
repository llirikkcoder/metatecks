
// Редактирование данных: адрес, профиль, безналичная оплата

function saveField(input, value) {
  var inputName = input.name,
      objectId = input.getAttribute('data-id'),
      objType = input.getAttribute('data-obj-type'),
      url = accountUrls.update[objType],
      data;

  data = {
    'data': {[inputName]: value},
    'id': objectId,
  }

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json',
    success: function(res){
      if (objType == 'user' && inputName == 'email') { updateCsrfToken(); }
      if (objType == 'user' && res['initials']) { $('.js-header-initials').html(res['initials']); }
    },
  });
}

var originalText;

$('.data_edit-btn').on('click', function(e){
  let editableDiv = this.closest('.data_editable');
  if (!editableDiv) return;
  editableDiv.classList.add('data_editing');

  let span = editableDiv.querySelector('.data_editable-text'),
      input = editableDiv.querySelector('input[type="text"]');
  if (!span || !input) return;

  // Сохраняем исходный текст
  originalText = span.textContent;
  input.value = originalText;

  input.focus();
});

$('.data_ok-btn').on('click', function(e){
  let editableDiv = this.closest('.data_editable');
  if (!editableDiv) return;

  let span = editableDiv.querySelector('.data_editable-text'),
      input = editableDiv.querySelector('input[type="text"]');
  if (!span || !input) return;

  let value = input.value;
  if (!value && input.required) {
    input.classList.add('error');
    return;
  }
  else {
    input.classList.remove('error');
    span.textContent = input.value;
    editableDiv.classList.remove('data_editing');
    saveField(input, value);
  }
});

$('.data_cancel-btn').on('click', function(e){
  let editableDiv = this.closest('.data_editable');
  if (!editableDiv) return;

  let span = editableDiv.querySelector('.data_editable-text'),
      input = editableDiv.querySelector('input[type="text"]');
  if (!span || !input) return;

  input.classList.remove('error');
  input.value = originalText; // Восстанавливаем исходный текст
  editableDiv.classList.remove('data_editing');
});


// Выбор одного из селектов: адрес, тип оплаты, карта для оплаты

$('.js-account-radio').on('change', function(e){
  var $input = $(this),
      value = $input.val(),
      objType = $input.data('obj-type'),
      url = accountUrls.select[objType],
      data;

  data = {'value': value}

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json',
  });
});


// Удаление объекта: адрес, карта для оплаты

$('.js-account-remove').on('click', function(e){
  var $button = $(this),
      objType = $button.data('obj-type'),
      value = $button.data('obj-id'),

      $container = $button.parents('.js-block-container'),
      $radio = $container.find('.js-account-radio'),
      wasChecked = $radio.is(':checked'),
      emptyDivSelector = $button.data('empty-div'),
      $emptyDiv = $(emptyDivSelector),

      confirmText = confirmTexts[objType],
      url = accountUrls.remove[objType],
      data;

  if (confirm(confirmText)) {
    data = {'value': value}
    $container.addClass('_disabled');

    $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify(data),
      dataType: 'json',
      contentType: 'application/json',
      success: function(res){
        $container.slideUp(300, function(){
          var $blocks = $(`.js-block-container[data-obj-type=${objType}]:visible`),
              blocksCount = $blocks.length;
          // если блоки еще есть, и мы удалили активный - отмечаем галкой первый
          if (blocksCount && wasChecked) {
            var $radio = $blocks.first().find('.js-account-radio');
            $radio.click();
          }
          // если блоков не осталось, показываем empty-блок
          else if (!blocksCount && $emptyDiv.length) {
            $emptyDiv.slideToggle();
          }
        });
      },
      error: function(){
        $container.removeClass('_disabled');
      }
    });
  }
});


// Отмена заказа

$('.js-cancel-button').on('click', function(e){
  var $button = $(this),
      objType = 'order',
      value = $button.data('obj-id'),
      number = $button.data('obj-number'),
      $container = $button.parents('.js-order-container'),
      confirmText = confirmTexts[objType],
      url = accountUrls.cancel[objType],
      data;

  if (confirm(confirmText)) {
    data = {'value': value}
    $container.addClass('_disabled');

    $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify(data),
      dataType: 'json',
      contentType: 'application/json',
      success: function(res){
        var redirectUrl = res['redirect_url'];
        if (redirectUrl) { window.location = redirectUrl; }
        else { alert(`Заказ № ${number} успешно отменен.`); }
      },
      complete: function(){
        $container.removeClass('_disabled');
      }
    });
  }
});


// Удаление/добавление в избранное

$('.js-favorite-checkbox').on('click', function(){
  var $checkbox = $(this);
  // $checkbox.change();

  var $label = $checkbox.parents('.js-favorite-label'),
      productId = $checkbox.data('product-id'),
      isChecked = $checkbox.is(':checked'),
      action = isChecked ? 'add' : 'remove',
      labelAfter = isChecked ? 'Удалить из избранного' : 'Добавить в избранное',
      url = accountUrls.favorites[action],
      data;

  data = {'product_id': productId};
  $label.attr('title', labelAfter);

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json',
  });
});


// Смена аватарки

var $avatarForm = $('#accountAvatarForm'),
    $avatarInput = $('input[name="avatar"]'),
    $avatarButton = $('.js-avatar-button'),
    $avatarContainer = $('.js-avatar-block');

$avatarForm.on('submit', function(e){
  e.preventDefault();
  var $form = $(this),
      url = $form.attr('action'),
      file = $avatarInput.get(0).files[0],
      formData = new FormData();

  formData.append('file', file);
  $avatarContainer.addClass('_disabled');

  $.ajax({
      url: url,
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      success: function(res){
        var accountAvatar = res['account_avatar'],
            headerAvatar = res['header_avatar'];
        $('.js-header-initials').hide();
        if (accountAvatar) { $('.js-account-avatar').attr('src', accountAvatar); }
        if (headerAvatar) { $('.js-header-avatar').css('background-image', `url("${headerAvatar}")`); }
      },
      complete: function(){
        $avatarContainer.removeClass('_disabled');
      }
   });
});

$avatarInput.change(function(){
  $avatarForm.submit();
});

$avatarButton.click(function(e){
  e.preventDefault();
  $avatarInput.click();
});
