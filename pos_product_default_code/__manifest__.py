# -*- coding: utf-8 -*-

{
    'name': 'PoS - Product default code',
    'version': '1.0',
    'author': 'Syentys',
    'license': 'OPL-1',
    'website': 'https://syentys.com',
    'category': 'Sales/Point Of Sale',
    'sequence': 6,
    'summary': 'Display default code in PoS',
    'description': """
""",
    'depends': ['point_of_sale'],
    'qweb': [
        'static/src/xml/pos_product_default_code.xml',
    ],
    'installable': True,
    'auto_install': False,
}
