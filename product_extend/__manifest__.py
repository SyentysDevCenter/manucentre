# -*- coding: utf-8 -*-

{
    "name": "Product extend",
    "version": "1.1",

    "depends": ['base', 'product', 'sale','stock_account'],

    "author": "ANDEMA",
    'website': 'http://www.andemaconulting.com',
    "category": "",
    "description": "",
    "init_xml": [],
    'data': [
        'wizard/product_dispatch_wizard.xml',
        'wizard/purchase_order_create.xml',

         'views/product_brand_view.xml',
         'views/product_margin.xml',
         'security/product_security.xml',
         'security/ir.model.access.csv',
        ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
