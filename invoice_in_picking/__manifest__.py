# -*- coding: utf-8 -*-

{
    'name': 'Invoice in picking',
    'version': '13.0.1.0',
    'author': 'Syentys',
    'website': 'www.syentys.fr',
    'depends': ['stock', 'stock_account','sale_stock','purchase_stock', 'sale','purchase','main_company'],
    'category': '',
    'demo': [],
    'data': [
        'wizard/stock_invoice_onshipping_view.xml',
        'views/stock_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
    ],
    'test': [

    ],
    'installable': True,
    'auto_install': True,
}
