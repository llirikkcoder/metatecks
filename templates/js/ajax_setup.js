// ----- AJAX setup: check cookies, set CSRF  -------


// Получаем из кук CSRF-токен и добавляем его к запросу

var csrfHiddenInput = document.querySelector('[name=csrfmiddlewaretoken]');
var csrftoken = csrfHiddenInput ? csrfHiddenInput.value : Cookies.get('csrftoken');

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function updateCsrfToken(){
  var _input = document.querySelector('[name=csrfmiddlewaretoken]');
  csrftoken = _input ? _input.value : Cookies.get('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        if (!areCookiesEnabled) {
          alertCookiesDisabled();
          return false;
        } else {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
        };
      }
    },
  });
}

updateCsrfToken();


// Обновляем количество товара в шапке

$(document).ajaxSuccess(function updateHeaderCartCount(event, xhr, options, data){
  function updateHeaderCartCount(quantity=0) {
    var $countSpan = $('#js-cart-count'),
        $countContainer = $('#js-basket-info');
    $countSpan.html(quantity);
    if (quantity) { $countContainer.show(); }
    else { $countContainer.hide(); }
  }

  if (data) {
    var cartCount = data['cart_count'];
    if (cartCount != undefined) { updateHeaderCartCount(cartCount); }
  }
})


// Выводим ошибку в модальном окне (#error-message из modals/error_message.html).
// Если модалки на странице нет — откатываемся на нативный alert.

function showErrorModal(message, title) {
  var $modal = $('#error-message');

  if (!$modal.length) { alert(message); return; }

  $modal.find('#js-error-message-title').text(title || 'Не удалось выполнить действие');
  $modal.find('#js-error-message').html(message);
  $modal.modal();
}

$(document).ajaxError(function myErrorHandler(event, res) {
  var status = res.status,
      statusText = res.statusText,
      response;

  if (res.responseJSON == undefined) { response = res.responseText; }
  else { response = res.responseJSON; }

  if (status == 400) {
    if (response != undefined) {
      var error = response['error'],
          alert_message = response['alert_message'];
      // текст из ответа сервера уже написан для покупателя — показываем как есть
      if (alert_message) { showErrorModal(alert_message); }
      else if (error) { showErrorModal(error); }
    }
    else {
      showErrorModal(`При отправке запроса произошла ошибка: ${status} ${statusText}`);
    };
  }
  else {
    if (status == 0) { showErrorModal('Сервис временно недоступен, попробуйте повторить попытку позже'); }
    else { showErrorModal(`Произошла ошибка: ${status} ${statusText}`); }
  }
});
