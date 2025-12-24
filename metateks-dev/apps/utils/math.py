from decimal import Decimal, ROUND_HALF_UP


def round_decimal(val, quantize=2):
    return Decimal(val.quantize(Decimal('.{}1'.format('0'*(quantize-1))), rounding=ROUND_HALF_UP))


def round_float(val, quantize=2):
    rounding = 10**quantize  # 100 в случае 2 точек после запятой
    return int(val*rounding)/rounding


def float_to_decimal(val, quantize=2):
    val = Decimal(float(val or 0.0))
    return round_decimal(val, quantize=quantize)


def get_percent_from_piece(ratio):
    return int(ratio*10000)/100.


def get_percent_ratio(value, ratio, _type='percent'):
    ratio = (
        get_percent_from_piece(ratio)
        if _type == 'piece'
        else ratio
    )
    return value * ratio/100.


def get_percent_value(value, ratio):
    piece = get_percent_ratio(value, ratio)
    return get_percent_from_piece(piece)


def get_percents(part, whole):
    percents = None if whole is None else 0
    if part and whole:
        percents = (part/whole) * 100
        percents = int(percents) if (int(percents) == percents) else percents
        if not isinstance(percents, int):
            percents = float(int(percents*100))/100
    return percents


def get_decimal_percent(decimal_value, ratio, _type='percent', quantize=None):
    """
    TODO FIXME: проверить округление при нецелых процентах в ratio
                (+ проверить влияние везде по проекту и поменять на _fixed вариант)
    """
    ratio = (
        get_percent_from_piece(ratio)
        if _type == 'piece'
        else ratio
    )
    value = decimal_value * float_to_decimal(ratio/100.)
    if quantize:
        value = round_decimal(value, quantize)
    return value


def get_decimal_percent_fixed(decimal_value, ratio, _type='percent', quantize=None):
    ratio = (
        get_percent_from_piece(ratio)
        if _type == 'piece'
        else ratio
    )
    value = decimal_value * float_to_decimal(ratio)/Decimal(100)
    if quantize:
        value = round_decimal(value, quantize)
    return value


def subtract_decimal_percent(decimal_value, ratio):
    """
    Вычитаем N% из decimal-значения
    """
    sub_value = get_decimal_percent_fixed(decimal_value, ratio, quantize=2)
    return decimal_value - sub_value
