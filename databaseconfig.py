#!/usr/bin/env python

source_connect = {
'SOURCE_HOST':"localhost",
'SOURCE_USER' : 'odoo',
'SOURCE_PASSWORD' : 'odoo',
'SOURCE_PORT': "5432",
'SOURCE_DB' :'MANU_LAST_DB',
'SOURCE_ODOO_USER': 'admin',
'SOURCE_ODOO_PASSWORD': 'a',
'ODOO_SOURCE_PORT': "8069"
}
dest_connect = {'DEST_ODOO_USER': 'admin',
                'DEST_ODOO_PASSWORD': 'a',
                'DEST_USER': 'odoo',
                'DEST_PASSWORD': 'odoo',
                'DEST_DB': 'MANUCENTRE_MIGRATION_PP_V2_T',
                'DEST_HOST': "localhost",
                'DEST_PORT': "5432",
                'ODOO_DEST_PORT': "8069"}

company_map = {
    '1':'1',
    '22':'4',
    '24':'2',
    '25':'3',
    '26':'4',
}

loc_map = {
    '1':'8',
    '22':'48',
    '24':'18',
    '25':'24',
    '26':'30',
}


property_account_receivable_map = {
    '1':'281',
    '2':'998',
    '3':'1715',
    '4':'2432',
}

property_account_payable_map = {
    '1':'267',
    '2':'984',
    '3':'1701',
    '4':'2418',
}

property_account_expense_categ_map = {
    '1':'425',
    '2':'1142',
    '3':'1859',
    '4':'2576',
}

property_account_income_categ_map = {
    '1':'631',
    '2':'1348',
    '3':'2065',
    '4':'2782',
}
