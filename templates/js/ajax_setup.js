// ----- AJAX setup: check cookies, set CSRF  -------


// Получаем из кук CSRF-токен и добавляем его к запросу

var csrftoken = Cookies.get('csrftoken');

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function updateCsrfToken(){
  csrftoken = Cookies.get('csrftoken');
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


// Выводим ошибку в алерте

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
      if (alert_message) { alert(alert_message); }
      else if (error) { alert(`При отправке запроса произошла ошибка: ${error}`); }
    }
    else {
      alert(`При отправке запроса произошла ошибка: ${status} ${statusText}`);
    };
  }
  else {
    if (status == 0) { alert('Произошла ошибка: 500 Internal Server Error'); }
    else { alert(`Произошла ошибка: ${status} ${statusText}`); }
  }
});
