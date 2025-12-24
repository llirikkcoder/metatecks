def get_order_number(order_id):
    if not order_id:
        return '0'
    if order_id > 1000:
        return '{:,}'.format(order_id).rjust(7, '0').replace(',', ' ')
    else:
        _number = '{:03}'.format(order_id)
        return '000 {}'.format(_number)
