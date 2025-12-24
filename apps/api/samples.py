CART_DATA_SAMPLE = {
    '1735': {
        'quantity': 5,
        'is_enabled': True,
        'warehouse_id': 1,
        'extra': {
            '1': {'quantity': 2, 'is_enabled': True},
            '2': {'quantity': 3, 'is_enabled': True},
        }
    },
    '1000': {
        'quantity': 1,
        'is_enabled': True,
        'warehouse_id': 2,
    }
}

ORDER_DATA_SAMPLE = {
    'delivery': {
        'method': 'company',
        'company_id': 2,
        'data': {
            'region': 'Волгоградская',
            'city': 'Волгоград',
            'address': 'Центральная, 5',
        },
    },
    'contacts': {
        'data': {
            'first_name': 'Петр',
            'patronymic_name': 'Петрович',
            'last_name': 'Петров',
            'phone': '+7 (951) 294-12-62',
        },
    },
    'payment': {
        'method': 'non_cash',
        'card_data': {},
        'non_cash_data': {
            'organization': 'ООО «‎Организация»',
            'inn': '2451 5235 1938 3278',
            'jur_address': 'г. Волгоград, ул. Центральная, 5',
        },
    },
}