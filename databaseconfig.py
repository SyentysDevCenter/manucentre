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
