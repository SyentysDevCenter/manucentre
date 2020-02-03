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
                'DEST_DB': 'MANUCENTRE_MIGRATION_SCRIPT_PRE_PROD',
                'DEST_HOST': "localhost",
                'DEST_PORT': "5432",
                'ODOO_DEST_PORT': "8069"}

company_map = {
    '1':'1',
    '22':'13',
    '24':'11',
    '25':'12',
    '26':'13',
}

loc_map = {
    '1':'8',
    '22':'144',
    '24':'112',
    '25':'122',
    '26':'132',
}


property_account_receivable_map = {
    '1':'281',
    '11':'12524',
    '12':'12523',
    '13':'12522',
}

property_account_payable_map = {
    '1':'267',
    '11':'12482',
    '12':'12481',
    '13':'12480',
}

property_account_expense_categ_map = {
    '1':'425',
    '11':'12965',
    '12':'12964',
    '13':'16653',
}

property_account_income_categ_map = {
    '1':'425',
    '11':'12965',
    '12':'12964',
    '13':'16653',
}
