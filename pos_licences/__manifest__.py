# -*- coding: utf-8 -*-
{
    'name': "Point of Sale Licences",

    'summary': """
        Display customers licences info in the POS module.""",

    'category': 'Point Of Sale',
    'version': '1.0',
    'author': 'SYENTYS',
    'website': 'http://www.syentys.com',
    'depends': ['point_of_sale','partner_extend'],
    'data': ['views/pos_licences_templates.xml'],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True
}
