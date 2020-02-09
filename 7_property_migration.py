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

def get_property_account_payable_id():
    try:
        connection = psycopg2.connect(user=SOURCE_USER,
                                      password=SOURCE_PASSWORD,
                                      host=SOURCE_HOST,
                                      port=SOURCE_PORT,
                                      database=SOURCE_DB)
        cursor = connection.cursor()
        query = f"select ir.company_id,CAST(SPLIT_PART(ir.value_reference,',',2) as INTEGER) as account, CAST(SPLIT_PART(ir.res_id,',',2) as INTEGER) " \
                f"as partner from ir_property ir where ir.name = 'property_account_payable_id' and ir.res_id is not null"
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

def get_property_account_receivable_id():
    try:
        connection = psycopg2.connect(user=SOURCE_USER,
                                      password=SOURCE_PASSWORD,
                                      host=SOURCE_HOST,
                                      port=SOURCE_PORT,
                                      database=SOURCE_DB)
        cursor = connection.cursor()
        query = f"select ir.company_id,CAST(SPLIT_PART(ir.value_reference,',',2) as INTEGER) as account, CAST(SPLIT_PART(ir.res_id,',',2) as INTEGER) " \
                f"as partner from ir_property ir where ir.name = 'property_account_receivable_id' and ir.res_id is not null"
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

def get_property_account_expense_categ_id():
    try:
        connection = psycopg2.connect(user=SOURCE_USER,
                                      password=SOURCE_PASSWORD,
                                      host=SOURCE_HOST,
                                      port=SOURCE_PORT,
                                      database=SOURCE_DB)
        cursor = connection.cursor()
        query = f"select ir.company_id,CAST(SPLIT_PART(ir.value_reference,',',2) as INTEGER) as account, CAST(SPLIT_PART(ir.res_id,',',2) as INTEGER) " \
                f"as categ from ir_property ir where ir.name = 'property_account_expense_categ_id' and ir.res_id is not null"
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

def get_property_account_income_categ_id():
    try:
        connection = psycopg2.connect(user=SOURCE_USER,
                                      password=SOURCE_PASSWORD,
                                      host=SOURCE_HOST,
                                      port=SOURCE_PORT,
                                      database=SOURCE_DB)
        cursor = connection.cursor()
        query = f"select ir.company_id,CAST(SPLIT_PART(ir.value_reference,',',2) as INTEGER) as account, CAST(SPLIT_PART(ir.res_id,',',2) as INTEGER) " \
                f"as categ from ir_property ir where ir.name = 'property_account_income_categ_id' and ir.res_id is not null"
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

def create_properties(properties):
    try:
        connection = psycopg2.connect(user=DEST_USER,
                                      password=DEST_PASSWORD,
                                      host=DEST_HOST,
                                      port=DEST_PORT,
                                      database=DEST_DB)

        cursor = connection.cursor()
        for p in properties:
            cursor.execute("INSERT INTO ir_property (name,res_id,fields_id,value_reference,type,company_id)"
                           "VALUES(%s, %s, %s, %s, %s,%s)",
                           (p[0], p[1], p[2], p[3], p[4], p[5]))
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

partner13 = odoov13.env['res.partner']
partners = partner13.search([('old_id', '!=', False)])
old_parts = partner13.read(partners, ['old_id'])
old_list_ids = {part['old_id']: part['id'] for part in old_parts}

category13 = odoov13.env['product.category']
categories = category13.search([('old_id', '!=', False)])
old_categs = category13.read(categories, ['old_id'])
old_categ_ids = {part['old_id']: part['id'] for part in old_categs}

account13 = odoov13.env['account.account']
accounts = account13.search([('old_id', '!=', False)])
old_accounts = account13.read(accounts, ['old_id'])
old_account_ids = {ac['old_id']: ac['id'] for ac in old_accounts}

# TODO finilaze properties importation
payment_term_field = odoov13.execute_kw('ir.model.data', 'get_object_reference',
                                        ['account', 'field_res_partner__property_payment_term_id'], {})
payment_term_supplier_field = odoov13.execute_kw('ir.model.data', 'get_object_reference',
                                                 ['account', 'field_res_partner__property_supplier_payment_term_id'],
                                                 {})
property_account_receivable_field = odoov13.execute_kw('ir.model.data', 'get_object_reference',
                                                       ['account', 'field_res_partner__property_account_receivable_id'],
                                                       {})
property_account_payable_field = odoov13.execute_kw('ir.model.data', 'get_object_reference',
                                                    ['account', 'field_res_partner__property_account_payable_id'], {})

property_account_expense_categ_field = odoov13.execute_kw('ir.model.data', 'get_object_reference',
                                                    ['account', 'field_product_category__property_account_expense_categ_id'], {})

property_account_income_categ_field = odoov13.execute_kw('ir.model.data', 'get_object_reference',
                                                    ['account', 'field_product_category__property_account_income_categ_id'], {})

# Import values from V9
property_account_payable_ids = get_property_account_payable_id()
property_account_payable_data = []
for pay_prop in property_account_payable_ids:
    if str(pay_prop[0]) in company_map.keys():
        if old_account_ids.get(pay_prop[1],False) and old_list_ids.get(pay_prop[2], False):
            account_payable_data = (
            'property_account_payable_id', 'res.partner,' + str(old_list_ids.get(pay_prop[2], False)),
            property_account_payable_field[1], 'account.account,' + str(old_account_ids.get(pay_prop[1],False)), "many2one",
            int(company_map[str(pay_prop[0])]))
            property_account_payable_data.append(account_payable_data)
create_properties(property_account_payable_data)

property_account_receivable_ids = get_property_account_receivable_id()
property_account_receivable_data = []
for rec_prop in  property_account_receivable_ids:
    if str(rec_prop[0]) in company_map.keys():
        if old_list_ids.get(rec_prop[2], False) and old_account_ids.get(rec_prop[1],False):
            account_receivable_data = (
            'property_account_receivable_id', 'res.partner,' + str(old_list_ids.get(rec_prop[2], False)),
            property_account_receivable_field[1], 'account.account,' + str(old_account_ids.get(rec_prop[1],False)), "many2one",
            int(company_map[str(rec_prop[0])]))
            property_account_receivable_data.append(account_receivable_data)
create_properties(property_account_receivable_data)

property_account_expense_categ_ids = get_property_account_expense_categ_id()
property_account_expense_categ_data = []
for cat_prop in  property_account_expense_categ_ids:
    if str(cat_prop[0]) in company_map.keys():
        if old_categ_ids.get(cat_prop[2], False) and old_account_ids.get(cat_prop[1],False):
            categ_res_id = 'product.category,' + str(old_categ_ids.get(cat_prop[2], False))
            account_expense_categ_data = (
            'property_account_expense_categ_id', categ_res_id,
            property_account_expense_categ_field[1], 'account.account,' + str(old_account_ids.get(cat_prop[1],False)), "many2one",
            int(company_map[str(cat_prop[0])]))
            property_account_expense_categ_data.append(account_expense_categ_data)
create_properties(property_account_expense_categ_data)

property_account_income_categ_id_ids = get_property_account_income_categ_id()
property_account_income_data = []
for cat_prop in  property_account_income_categ_id_ids:
    if str(cat_prop[0]) in company_map.keys():
        if old_categ_ids.get(cat_prop[2], False) and old_account_ids.get(cat_prop[1],False):
            categ_res_id = 'product.category,' + str(old_categ_ids.get(cat_prop[2], False))
            account_income_categ_data = (
            'property_account_income_categ_id', categ_res_id,
            property_account_expense_categ_field[1], 'account.account,' + str(old_account_ids.get(cat_prop[1],False)), "many2one",
            int(company_map[str(cat_prop[0])]))
            property_account_income_data.append(account_income_categ_data)
create_properties(property_account_income_data)

# Create default values
def_property_account_payable_data = []
for comp in set(company_map.values()):
    account_payable_data = (
        'property_account_payable_id', None,
        property_account_payable_field[1], 'account.account,' + str(property_account_payable_map.get(comp)), "many2one",
        int(comp))
    def_property_account_payable_data.append(account_payable_data)
create_properties(def_property_account_payable_data)

# Create default values
def_property_account_receivable_data = []
for comp in set(company_map.values()):
    account_receivable_data = (
        'property_account_receivable_id', None,
        property_account_receivable_field[1], 'account.account,' + str(property_account_receivable_map.get(comp)), "many2one",
        int(comp))
    def_property_account_receivable_data.append(account_receivable_data)
create_properties(def_property_account_receivable_data)

# Create default values
def_property_account_expense_categ_data = []
for comp in set(company_map.values()):
    account_expense_categ_data = (
        'property_account_expense_categ_id', None,
        property_account_expense_categ_field[1], 'account.account,' + str(property_account_expense_categ_map.get(comp)), "many2one",
        int(comp))
    def_property_account_expense_categ_data.append(account_expense_categ_data)
create_properties(def_property_account_expense_categ_data)

# Create default values
def_property_account_income_categ_data = []
for comp in set(company_map.values()):
    account_income_categ_data = (
        'property_account_income_categ_id', None,
        property_account_income_categ_field[1], 'account.account,' + str(property_account_income_categ_map.get(comp)), "many2one",
        int(comp))
    def_property_account_income_categ_data.append(account_income_categ_data)
create_properties(def_property_account_income_categ_data)
