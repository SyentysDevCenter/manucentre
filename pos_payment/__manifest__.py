# -*- coding: utf-8 -*-

{
    "name": "Pos payement",
    "version": "1.0",

    "depends": ['point_of_sale', 'product', 'sale','account'],

    "author": "ANDEMA",
    'website': 'http://www.andemaconulting.com',
    "category": "",
    "description": "",
    "init_xml": [],
    'data': [
         'views/payment.xml',
         'security/ir.model.access.csv',
        ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
