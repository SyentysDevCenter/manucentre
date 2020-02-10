import odoorpc
import psycopg2
from datetime import date, datetime
import databaseconfig as cfg

# SOURCE
SOURCE_HOST =cfg.source_connect['SOURCE_HOST']
SOURCE_USER =cfg.source_connect['SOURCE_USER']
SOURCE_PASSWORD = cfg.source_connect['SOURCE_PASSWORD']
SOURCE_PORT = cfg.source_connect['SOURCE_PORT']
SOURCE_DB = cfg.source_connect['SOURCE_DB']

# DEST
DEST_ODOO_USER =cfg.dest_connect['DEST_ODOO_USER']
DEST_ODOO_PASSWORD = cfg.dest_connect['DEST_ODOO_PASSWORD']
DEST_USER = cfg.dest_connect['DEST_USER']
DEST_PASSWORD = cfg.dest_connect['DEST_PASSWORD']
DEST_DB = cfg.dest_connect['DEST_DB']
DEST_HOST = cfg.dest_connect['DEST_HOST']
DEST_PORT = cfg.dest_connect['DEST_PORT']
ODOO_DEST_PORT = cfg.dest_connect['ODOO_DEST_PORT']

# Mapping
company_map = cfg.company_map
property_account_receivable_map = cfg.property_account_receivable_map
property_account_payable_map = cfg.property_account_payable_map
property_account_expense_categ_map = cfg.property_account_expense_categ_map
property_account_income_categ_map = cfg.property_account_income_categ_map

def get_taxes():
    try:
        connection = psycopg2.connect(user=SOURCE_USER,
                                      password=SOURCE_PASSWORD,
                                      host=SOURCE_HOST,
                                      port=SOURCE_PORT,
                                      database=SOURCE_DB)
        cursor = connection.cursor()
        query = "select act.amount,act.company_id,rel.prod_id from product_taxes_rel rel, account_tax act " \
                "where act.id = rel.tax_id " \
                "order by rel.prod_id"
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

def get_supplier_taxes():
    try:
        connection = psycopg2.connect(user=SOURCE_USER,
                                      password=SOURCE_PASSWORD,
                                      host=SOURCE_HOST,
                                      port=SOURCE_PORT,
                                      database=SOURCE_DB)
        cursor = connection.cursor()
        query = "select act.amount,act.company_id,rel.prod_id from product_supplier_taxes_rel rel, account_tax act " \
                "where act.id = rel.tax_id " \
                "order by rel.prod_id"
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

def create_taxes(taxes):
    try:
        connection = psycopg2.connect(user=DEST_USER,
                                      password=DEST_PASSWORD,
                                      host=DEST_HOST,
                                      port=DEST_PORT,
                                      database=DEST_DB)

        cursor = connection.cursor()
        for tax in taxes:
            cursor.execute("INSERT INTO product_taxes_rel (prod_id,tax_id)"
                           "VALUES(%s, %s)",
                           (tax[0], tax[1]))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

def create_supplier_taxes(taxes):
    try:
        connection = psycopg2.connect(user=DEST_USER,
                                      password=DEST_PASSWORD,
                                      host=DEST_HOST,
                                      port=DEST_PORT,
                                      database=DEST_DB)

        cursor = connection.cursor()
        for tax in taxes:
            cursor.execute("INSERT INTO product_supplier_taxes_rel (prod_id,tax_id)"
                           "VALUES(%s, %s)",
                           (tax[0], tax[1]))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()


# Login to destination server
odoov13 = odoorpc.ODOO(DEST_HOST, port=ODOO_DEST_PORT)
odoov13.login(DEST_DB, DEST_ODOO_USER, DEST_ODOO_PASSWORD)

product_prod = odoov13.env['product.template']
product_prod_ids = product_prod.search(['|', ('active', '=', True), ('active', '=', False)])
product_prod_data = product_prod.read(product_prod_ids, ['old_id'])
dict_product_prod = {part['old_id']: part['id'] for part in product_prod_data}

tax_dict = {
    '0.0000-1': 52,
    '5.5000-1': 15,
    '10.0000-1': 14,
    '20.0000-1': 1,
    '0.0000-2': 107,
    '5.5000-2': 70,
    '10.0000-2': 69,
    '20.0000-2': 56,
    '0.0000-3': 162,
    '5.5000-3': 125,
    '10.0000-3': 124,
    '20.0000-3': 111,
    '0.0000-4': 217,
    '5.5000-4': 180,
    '10.0000-4': 179,
    '20.0000-4': 166,
}

supplier_tax_dict = {
    '0.0000-1': 55,
    '5.5000-1': 25,
    '10.0000-1': 21,
    '20.0000-1': 19,
    '0.0000-2': 110,
    '5.5000-2': 80,
    '10.0000-2': 76,
    '20.0000-2': 74,
    '0.0000-3': 165,
    '5.5000-3': 135,
    '10.0000-3': 131,
    '20.0000-3': 129,
    '0.0000-4': 220,
    '5.5000-4': 190,
    '10.0000-4': 186,
    '20.0000-4': 184,
}

taxes_ids = get_taxes()
taxes_data = set()
for tax in taxes_ids:
    if str(tax[1]) in company_map.keys():
        if dict_product_prod.get(tax[2],False):
            tax_id = tax_dict.get('-'.join([str(tax[0]),company_map.get(str(tax[1]),False)]),False)
            if tax_id:
                tax_data = (
                    dict_product_prod.get(tax[2], False),tax_id
                )
                taxes_data.add(tax_data)
create_taxes(taxes_data)

supplier_taxes_ids = get_supplier_taxes()
supplier_taxes_data = set()
for tax in supplier_taxes_ids:
    if str(tax[1]) in company_map.keys():
        if dict_product_prod.get(tax[2],False):
            tax_id = supplier_tax_dict.get('-'.join([str(tax[0]),company_map.get(str(tax[1]),False)]),False)
            if tax_id:
                tax_data = (
                    dict_product_prod.get(tax[2], False),tax_id
                )
                supplier_taxes_data.add(tax_data)
create_supplier_taxes(supplier_taxes_data)