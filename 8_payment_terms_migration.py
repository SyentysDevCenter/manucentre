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

def get_property_payment_term_id():
    try:
        connection = psycopg2.connect(user=SOURCE_USER,
                                      password=SOURCE_PASSWORD,
                                      host=SOURCE_HOST,
                                      port=SOURCE_PORT,
                                      database=SOURCE_DB)
        cursor = connection.cursor()
        query = "select ir.company_id,pt.name,CAST(SPLIT_PART(ir.value_reference,',',2) as INTEGER) as payement_term, " \
                "CAST(SPLIT_PART(ir.res_id,',',2) as INTEGER) as partner " \
                "from ir_property ir, account_payment_term pt " \
                "where ir.name = 'property_payment_term_id' " \
                "and ir.res_id is not null and CAST(SPLIT_PART(ir.value_reference,',',2) as INTEGER) = pt.id"
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

def get_property_supplier_payment_term_id():
    try:
        connection = psycopg2.connect(user=SOURCE_USER,
                                      password=SOURCE_PASSWORD,
                                      host=SOURCE_HOST,
                                      port=SOURCE_PORT,
                                      database=SOURCE_DB)
        cursor = connection.cursor()
        query = "select ir.company_id,pt.name,CAST(SPLIT_PART(ir.value_reference,',',2) as INTEGER) as payement_term, " \
                "CAST(SPLIT_PART(ir.res_id,',',2) as INTEGER) as partner " \
                "from ir_property ir, account_payment_term pt " \
                "where ir.name = 'property_supplier_payment_term_id' " \
                "and ir.res_id is not null and CAST(SPLIT_PART(ir.value_reference,',',2) as INTEGER) = pt.id"
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

payemnt_terms_13 = odoov13.env['account.payment.term']
payemnt_terms = payemnt_terms_13.search([])
payemnt_terms_data = payemnt_terms_13.read(payemnt_terms, ['name'])
payemnt_terms_ids = {part['name']: part['id'] for part in payemnt_terms_data}

payment_term_field = odoov13.execute_kw('ir.model.data', 'get_object_reference',
                                        ['account', 'field_res_partner__property_payment_term_id'], {})
payment_term_supplier_field = odoov13.execute_kw('ir.model.data', 'get_object_reference',
                                                 ['account', 'field_res_partner__property_supplier_payment_term_id'],
                                                 {})

property_payment_term_ids = get_property_payment_term_id()
property_payment_term_data = []
for pay_prop in property_payment_term_ids:
    if str(pay_prop[0]) in company_map.keys():
        if payemnt_terms_ids.get(pay_prop[1],False):
            account_payable_data = (
            'property_payment_term_id', 'res.partner,' + str(old_list_ids.get(pay_prop[3], False)),
            payment_term_field[1], 'account.payment.term,' + str(payemnt_terms_ids.get(pay_prop[1],False)), "many2one",
            int(company_map[str(pay_prop[0])]))
            property_payment_term_data.append(account_payable_data)
create_properties(property_payment_term_data)

property_supplier_payment_term_ids = get_property_supplier_payment_term_id()
property_supplier_payment_term_data = []
for pay_prop in property_supplier_payment_term_ids:
    if str(pay_prop[0]) in company_map.keys():
        if payemnt_terms_ids.get(pay_prop[1],False):
            account__supplier_payable_data = (
            'property_supplier_payment_term_id', 'res.partner,' + str(old_list_ids.get(pay_prop[3], False)),
            payment_term_field[1], 'account.payment.term,' + str(payemnt_terms_ids.get(pay_prop[1],False)), "many2one",
            int(company_map[str(pay_prop[0])]))
            property_supplier_payment_term_data.append(account__supplier_payable_data)
create_properties(property_supplier_payment_term_data)
