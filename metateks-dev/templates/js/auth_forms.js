// ----- Формы логина/регистрации на бекенд -----

$('.js-auth-form').on('submit', function(e) {
  e.preventDefault();

  var $form = $(this),
      $authForms = $('.js-auth-form'),
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
      $authForms.removeClass('_disabled');
    }
  });
});
