
var $productContainer = $('#js-product-container'),
    productId = $productContainer.data('product-id'),
    isAdded = $productContainer.data('is-added');
var $priceItem = $('#js-price'),
    price = parseInt($priceItem.data('price'));
var $extraCheckboxes = $('input.js-extra-checkbox');
var cartButtonSelector = 'a.js-cart-button';
    buyButtonSelector = 'a.js-buy-button';
var $totalSpan = $('#js-total');


function updateTotal(){
  var total = price;
  $extraCheckboxes.each(function(index, checkbox){
    if (checkbox.checked) {
      var extraPrice = parseInt(checkbox.getAttribute('data-price'));
      total += extraPrice;
    }
  });
  total = total.toLocaleString('ru-RU') + ' ₽';
  $totalSpan.html(total);
}

updateTotal();


function addItem(buttonType='cart'){
  var warehouseId = $('input[name="storage-option"]:checked').val(),
      $extraChecked = $('input.js-extra-checkbox:checked'),
      extraIds = [],
      url = urls.product,
      cartUrl = urls.cart,
      $cartButton = $(cartButtonSelector),
      $buyButton = $(buyButtonSelector);
  var data = {'product_id': productId};

  if (warehouseId) { data['warehouse_id'] = parseInt(warehouseId); }
  if ($extraChecked) {
    $extraChecked.each(function(index, checkbox){
      extraIds.push(checkbox.getAttribute('data-extra-id'));
    });
    data['extra_ids'] = extraIds;
  }

  $productContainer.addClass('_disabled');

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json',
    success: function(res){
      isAdded = true;
      $productContainer.data('is-added', true);
      $cartButton.addClass('_disabled');
      $cartButton.find('.label').html('В корзине');
      $buyButton.attr('href', cartUrl);
      $buyButton.removeClass('js-buy-button');
      if (buttonType == 'cart'){ $('#product-added').modal(); }
      else { window.location = urls.cart; }
    },
    complete: function(){
      $productContainer.removeClass('_disabled');
    }
  });
}


function updateExtraItem($checkbox){
  var $container = $checkbox.parents('.js-extra-container'),
      extraId = $checkbox.data('extra-id'),
      isChecked = $checkbox.is(':checked'),
      quantity = isChecked ? 1 : 0,
      url = urls['extra'];
  var data = {'product_id': productId, 'extra_id': extraId, 'quantity': quantity};

  $container.addClass('_disabled');

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json',
    complete: function(){
      $container.removeClass('_disabled');
    }
  });
}


$('body').on('click', cartButtonSelector, function(e){
  e.preventDefault();
  addItem(buttonType='cart');
});


$('body').on('click', buyButtonSelector, function(e){
  e.preventDefault();
  addItem(buttonType='buy');
});


$extraCheckboxes.on('change', function(e) {
  updateTotal();
  if (isAdded) {
    var $checkbox = $(this);
    updateExtraItem($checkbox);
  }
});


$('.js-favorite-checkbox').on('change', function(){
  var $checkbox = $(this),
      $label = $checkbox.parents('.js-favorite-label'),
      productId = $checkbox.data('product-id'),
      isChecked = $checkbox.is(':checked'),
      action = isChecked ? 'add' : 'remove',
      labelAfter = isChecked ? 'Удалить из избранного' : 'Добавить в избранное',
      url = urls.favorites[action],
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
