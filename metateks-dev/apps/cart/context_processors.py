
def cart(request):
    if request.path.startswith('/admin/'):
        return {}

    cart_count = request.session.get('cart_count')
    return {'cart_count': cart_count}
