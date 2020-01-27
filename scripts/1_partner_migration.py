import odoorpc
import psycopg2
from datetime import date, datetime

#SOURCE
SOURCE_HOST = "localhost"
SOURCE_USER = 'odoo'
SOURCE_PASSWORD = 'odoo'
SOURCE_PORT = "5432"
SOURCE_DB = 'MANU_LAST_DB'

#DEST
DEST_ODOO_USER = 'admin'
DEST_ODOO_PASSWORD = 'a'
DEST_USER = 'odoo'
DEST_PASSWORD = 'odoo'
DEST_DB = 'MANUCENTRE_MIGRATION_SCRIPT_T2'
DEST_HOST = "localhost"
DEST_PORT = "5432"
ODOO_DEST_PORT = "8069"

#Company_mapping
company_map = {
    '1':'1',
    '22':'13',
    '24':'11',
    '25':'12',
    '26':'13',
}


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

def get_payment_term():
    try:
        connection = psycopg2.connect(user=SOURCE_USER,
                                      password=SOURCE_PASSWORD,
                                      host=SOURCE_HOST,
                                      port=SOURCE_PORT,
                                      database=SOURCE_DB)
        cursor = connection.cursor()
        query = f"select ac.id,ac.name,ac.note,apl.value,apl.value_amount,apl.days, apl.option," \
                f"apl.sequence from account_payment_term_line apl,account_payment_term ac where apl.payment_id = ac.id " \
                f"and apl.payment_id in (select id from account_payment_term where active=True)"
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
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in properties:
            cursor.execute("INSERT INTO ir_property (name,res_id,fields_id,value_reference,type,company_id)"
                           "VALUES(%s, %s, %s, %s, %s,%s)",
                           (p[0],p[1],p[2],p[3],p[4],p[5]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def set_parents(partners):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in partners:
            cursor.execute("update res_partner set parent_id = %s where old_id = %s",
                           (p[0],p[1]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def create_partners(partners):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in partners:
            cursor.execute("INSERT INTO res_partner (name, is_company, ref, street, street2, zip, city, function,"
                           " phone,mobile, fax, email, old_id,"                           
                           "customer_rank, supplier_rank, active, hunting_licence_number, hunting_licence_date, "
                           "hunting_licence_validity, hunting_oncfs, hunting_state, shooting_licence, "
                           "shooting_licence_validity, shooting_club_number, "
                           "shooting_club_name, balltrap_licence, balltrap_licence_validity, balltrap_club_number, "
                           "balltrap_club_name, siret, display_name)"
                           "VALUES(%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
                           ", %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                           (p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12], p[13]
                            , p[14], p[15], p[16], p[17], p[18], p[19],p[20], p[21], p[22], p[23], p[24], p[25], p[26]
                            , p[27], p[28], p[29], p[30]))

        connection.commit()

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()


def get_partners():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)

        cursor = connection.cursor()
        query = f"select p.name, p.is_company, p.ref, p.street, p.street2, p.zip, p.city, p.function, p.phone, p.mobile," \
                f"p.fax, p.email, p.id, " \
                f"p.customer, p.supplier, p.active, p.hunting_licence_number, p.hunting_licence_date, p.hunting_licence_validity," \
                f"p.hunting_oncfs, p.hunting_state, p.shooting_licence, p.shooting_licence_validity, p.shooting_club_number," \
                f"p.shooting_club_name, p.balltrap_licence, p.balltrap_licence_validity, p.balltrap_club_number," \
                f"p.balltrap_club_name, p.siret, p.display_name, parent_id," \
                f"CAST(SPLIT_PART(ir.value_reference,',',2) as INTEGER),CAST(SPLIT_PART(ir2.value_reference,',',2) as INTEGER)" \
                f" from res_partner p LEFT OUTER JOIN ir_property ir ON p.ID = CAST(SPLIT_PART(ir.res_id,',',2) as INTEGER)" \
                f" and ir.name ='property_account_payable_id' LEFT OUTER JOIN ir_property ir2 ON p.ID = CAST(SPLIT_PART(ir2.res_id,',',2) as INTEGER) " \
                f" and ir2.name ='property_account_receivable_id' " \
                f"ORDER BY p.id"
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

# Login to destination server
odoov13 = odoorpc.ODOO(DEST_HOST, port=ODOO_DEST_PORT)
odoov13.login(DEST_DB, DEST_ODOO_USER, DEST_ODOO_PASSWORD)

pay_terms = get_payment_term()
account_payment_term_obj = odoov13.env['account.payment.term']
current_pay_ids = account_payment_term_obj.search([])
account_payment_term_obj.browse(current_pay_ids).unlink()

payment_ids = {}
for pay in pay_terms:
    if not payment_ids.get(str(pay[0]),False):
        result = odoov13.execute(
            'account.payment.term', 'create',
            {
                'name': pay[1],
                'note': pay[2],
                'old_id':pay[0],
            })
        payment_ids[str(pay[0])] = result
    option = pay[6]
    options = ['day_after_invoice_date','day_following_month','day_current_month']
    if not option in options:
        option = 'day_after_invoice_date'
    result = odoov13.execute(
        'account.payment.term.line', 'create',
        {
            'value': pay[3],
            'value_amount': float(pay[4]),
            'days': int(pay[5]),
            'option': option,
            'sequence': int(pay[7]),
            'payment_id': int(payment_ids.get(str(pay[0]),None)),
        })

new_pt_ids = account_payment_term_obj.search([])
pay_term_data = account_payment_term_obj.read(new_pt_ids, ['old_id'])
dict_pay_term = {pt['old_id']:pt['id'] for pt in pay_term_data}


"""
payment_term = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['account', 'account_payment_term_30days'], {})

account = odoov13.env['account.account']

customer = account.search([('code','=','411100')],limit=1)
if not customer:
    raise Exception('No customer account is defined!')
supplier = account.search([('code','=','401100')],limit=1)
if not supplier:
    raise Exception('No supplier account is defined!')
print("customer,supplier",customer,supplier)

res_state = odoov13.env['res.country.state']
state_ids = res_state.search([])
state_data = res_state.read(state_ids, ['old_id'])
dict_state = {part['old_id']:part['id'] for part in state_data}

partner13 = odoov13.env['res.partner']
account_ids = account.search([])
account_data = account.read(account_ids, ['old_id'])
dict_account = {acc['old_id']:acc['id'] for acc in account_data}
"""

res_state = odoov13.env['res.country.state']
state_ids = res_state.search([])
state_data = res_state.read(state_ids, ['old_id'])
dict_state = {part['old_id']:part['id'] for part in state_data}

list_data = []

for part in get_partners():
    date_delivr = None
    if isinstance(part[17], (datetime, date)):
        date_delivr = part[17].isoformat()
    siret =None
    if part[29] != None:
        siret = part[29][:14]
    data = (part[0], part[1], part[2], part[3], part[4], part[5], part[6], part[7], part[8], part[9], part[10], part[11], part[12],
            1 if part[13] else 0, 1 if part[14] else 0, part[15],part[16],date_delivr,part[18],part[19],
            dict_state.get(part[20], None),part[21],part[22],part[23],part[24],part[25],part[26],part[27],part[28],siret,part[30])
    list_data.append(data)
create_partners(list_data)

partner13 = odoov13.env['res.partner']
partners = partner13.search([('old_id', '!=', False)])
old_parts = partner13.read(partners, ['old_id'])
old_list_ids = {part['old_id']: part['id'] for part in old_parts}

parents = []
for p in get_partners():
    if p[31]!= None:
        data = (old_list_ids[p[31]], p[12])
        parents.append(data)
set_parents(parents)

account13 = odoov13.env['account.account']
accounts = account13.search([('old_id', '!=', False)])
old_accounts = account13.read(accounts, ['old_id'])
old_account_ids = {ac['old_id']: ac['id'] for ac in old_accounts}

#TODO finilaze properties importation
payment_term_field = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['account', 'field_res_partner__property_payment_term_id'], {})
payment_term_supplier_field = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['account', 'field_res_partner__property_supplier_payment_term_id'], {})
property_account_receivable_field = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['account', 'field_res_partner__property_account_receivable_id'], {})
property_account_payable_field = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['account', 'field_res_partner__property_account_payable_id'], {})

property_account_payable_ids = get_property_account_payable_id()

property_account_payable_data = []
for pay_prop in property_account_payable_ids:
    if str(pay_prop[0]) in company_map.keys():
        account_payable_data = ('property_account_payable_id', 'res.partner,' + str(old_list_ids.get(pay_prop[2], False)),
                                property_account_payable_field[1], 'account.account,' + str(pay_prop[1]), "many2one",int(company_map[str(pay_prop[0])]))
        property_account_payable_data.append(account_payable_data)
create_properties(property_account_payable_data)

"""
data_payment_term_data = []
data_payment_supplier_term_data = []
property_account_receivable_data = []
property_account_payable_data = []

payment_term_field = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['account', 'field_res_partner__property_payment_term_id'], {})
payment_term_supplier_field = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['account', 'field_res_partner__property_supplier_payment_term_id'], {})
property_account_receivable_field = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['account', 'field_res_partner__property_account_receivable_id'], {})
property_account_payable_field = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['account', 'field_res_partner__property_account_payable_id'], {})
partners = partner13.search([('old_id', '!=', False)])

old_parts = partner13.read(partners, ['old_id'])
old_list_ids = {part['old_id']:part['id'] for part in old_parts}
#

for d in accounts_data:
    payment_data = ('property_payment_term_id', 'res.partner,'+str(old_list_ids.get(d[0], False)),payment_term_field[1],'account.payment.term,'+str(payment_term[1]),"many2one")
    payment_supplier_data = ('property_supplier_payment_term_id', 'res.partner,'+str(old_list_ids.get(d[0], False)),payment_term_supplier_field[1],'account.payment.term,'+str(payment_term[1]),"many2one")
    account_receivable_data = ('property_account_receivable_id', 'res.partner,'+str(old_list_ids.get(d[0], False)), property_account_receivable_field[1],'account.account,'+str(d[2]),"many2one")
    account_payable_data = ('property_account_payable_id','res.partner,'+str(old_list_ids.get(d[0], False)),property_account_payable_field[1],'account.account,'+str(d[1]),"many2one")
    data_payment_term_data.append(payment_data)
    data_payment_supplier_term_data.append(payment_supplier_data)
    property_account_receivable_data.append(account_receivable_data)
    property_account_payable_data.append(account_payable_data)
    
create_properties(data_payment_term_data)
create_properties(data_payment_supplier_term_data)
create_properties(property_account_receivable_data)
create_properties(property_account_payable_data)
"""