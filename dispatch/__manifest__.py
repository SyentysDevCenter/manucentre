# -*- coding: utf-8 -*-

{
    'name': 'Dispatching',
    'summary': '',
    'description': """
    """,
    'version': '0.1',
    'author': 'SYENTYS',
    'website': 'http://www.syentys.com',
    'category': 'Inventory',
    'depends': ['sale_management', 'purchase', 'stock', 'inter_company_rules'],
    'data': [
        'wizard/stock_dispatch_wizard.xml',
        'data/sequence.xml',
        'views/stock_picking_views.xml',
        'views/stock_dispatch_views.xml',
        'views/product_category_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False
}