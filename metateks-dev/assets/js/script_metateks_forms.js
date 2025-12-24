// ----- Отправка форм на бекенд: базовые функции -----

function getFormData($form){
  var unindexed_array = $form.serializeArray();
  var indexed_array = {};

  $.map(unindexed_array, function(n, i){ indexed_array[n['name']] = n['value']; });
  return indexed_array;
};


function removeErrors($form) {
  $form.find('.error').removeClass('error');
  $form.find('.err-message').remove();
  $form.find('.error-messages').hide();
  $form.find('.error-messages').html('');
}


function addErrors($form, errors, without_errors, without_names) {
  var $errorMessages = $form.find('.error-messages'),
      without_errors = without_errors || false,
      without_names = without_names || false,
      errorsPrepend = $form.hasClass('js-field-errors-prepend');

  if (!errors.length) {
    alert('При отправке запроса произошла ошибка');
    return;
  }

  errors.forEach(function(item, i, list) {
    var error = item.error_message,
        name = item.label || item.name;

    if (name == '__all__') {
      if (error && !without_errors) {
        $errorMessages.show();
        $errorMessages.append(`<div>${error}</div>`);
      };
    } else {
      var $field = $form.find('[name="'+item.name+'"]'),
          $parent = $field.parents('.field-row');
      $field.addClass('error');
      if (error && !without_errors) {
        if ($parent) {
          var errorHTML = '<div class="err-message">' + error + '<br/></div>';
          if (errorsPrepend) { $parent.prepend(errorHTML); }
          else { $parent.before(errorHTML); }
        }
        else {
          $errorMessages.show();
          if (without_names) { $errorMessages.append(`<div>${error}</div>`); }
          else { $errorMessages.append(`<div>${name}: ${error}</div>`) }
        }
      }
    }
  });
}


// ----- Отправка форм на бекенд: отправка обычной формы -----

$(document).ready(function(){
  $('body').on('submit', '.js-regular-form', function(e) {
    e.preventDefault();

    var $form = $(this),
        url = $form.attr('action'),
        form_data;

    form_data = getFormData($form);
    removeErrors($form);

    $form.addClass('_disabled');

    $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify(form_data),
      dataType: 'json',
      contentType: 'application/json',

      success: function(res){
        var next = res['redirect_url'];
        if (next) { window.location = next; }
        else { window.location.reload(); }
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
        $form.removeClass('_disabled');
      }
    });
  });
})
