import odoorpc
import psycopg2
from datetime import date, datetime
USER = 'odoo13'
PASSWORD = 'odoo'
USER_source = 'openpg'
PASSWORD_source = 'openpgpwd'
HOST = "127.0.0.1"
Port_source = "5433"
Port_dest = "5432"
DB_souce = 'manucentre_last9'
DB_dest = 'manucentre2'

#
# def get_companies():
#     try:
#         connection = psycopg2.connect(user = USER_source,
#                                       password = PASSWORD_source,
#                                       host = HOST,
#                                       port = Port_source,
#                                       database = DB_souce)
#
#         cursor = connection.cursor()
#         query = """
#                 select name,partner_id, currency_id
#                 from res_company;
#                 """
#         cursor.execute(query)
#         record = cursor.fetchall()
#         return record
#
#     except (Exception, psycopg2.Error) as error :
#         print ("Error while connecting to PostgreSQL", error)
#     finally:
#             if(connection):
#                 cursor.close()
#                 connection.close()
#
# def create_companies(prices):
#     try:
#         connection = psycopg2.connect(user = USER,
#                                       password = PASSWORD,
#                                       host = HOST,
#                                       port = Port_dest,
#                                       database = DB_dest)
#
#         cursor = connection.cursor()
#         for p in prices:
#             cursor.execute("INSERT INTO res_company (name,partner_id, currency_id)"
#                            "VALUES(%s, %s)",
#                            (p[0],p[1]))
#         connection.commit()
#     except (Exception, psycopg2.Error) as error :
#         print ("Error while connecting to PostgreSQL", error)
#     finally:
#             if(connection):
#                 cursor.close()
#                 connection.close()

def create_properties(properties):
    try:
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

        cursor = connection.cursor()
        # property_payment_term_id
        for p in properties:
            cursor.execute("INSERT INTO ir_property (name,res_id, company_id,fields_id,value_reference,type)"
                           "VALUES(%s, %s, 1, %s, %s, %s)",
                           (p[0],p[1],p[2],p[3],p[4]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def set_parents(partners):
    try:
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

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
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

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


def get_partners(partner_ids):
    if not partner_ids:
        return []
    try:
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)

        cursor = connection.cursor()
        # print(tuple(partner_ids,))
        query = f"select p.name, p.is_company, p.ref, p.street, p.street2, p.zip, p.city, p.function, p.phone, p.mobile," \
                f"p.fax, p.email, p.id, " \
                f"p.customer, p.supplier, p.active, p.hunting_licence_number, p.hunting_licence_date, p.hunting_licence_validity," \
                f"p.hunting_oncfs, p.hunting_state, p.shooting_licence, p.shooting_licence_validity, p.shooting_club_number," \
                f"p.shooting_club_name, p.balltrap_licence, p.balltrap_licence_validity, p.balltrap_club_number," \
                f"p.balltrap_club_name, p.siret, p.display_name, parent_id," \
                f"CAST(SPLIT_PART(ir.value_reference,',',2) as INTEGER),CAST(SPLIT_PART(ir2.value_reference,',',2) as INTEGER)" \
                f" from res_partner p LEFT OUTER JOIN ir_property ir ON p.ID = CAST(SPLIT_PART(ir.res_id,',',2) as INTEGER)" \
                f" and ir.name ='property_account_payable_id' LEFT OUTER JOIN ir_property ir2 ON p.ID = CAST(SPLIT_PART(ir2.res_id,',',2) as INTEGER) " \
                f" and ir2.name ='property_account_receivable_id'  where p.id in {tuple(partner_ids)}" \
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

# Login to source server
odoo = odoorpc.ODOO('localhost', port="8091")
odoo.login("manucentre_last9", 'admin', 'a')

# Login to destination server
odoov13 = odoorpc.ODOO('localhost', port="8069")
odoov13.login("manucentre2", 'admin', 'a')

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

partner = odoo.env['res.partner']
partner13 = odoov13.env['res.partner']
account_ids = account.search([])
account_data = account.read(account_ids, ['old_id'])
dict_account = {acc['old_id']:acc['id'] for acc in account_data}


offset = 0
old_list = []
accounts_data = []
for i in range(40):
    partner_ids = partner.search([], offset=offset, limit=2000)
    offset += 2000
    list_data = []

    for part in get_partners(partner_ids):
        # partner13_old = partner13.search([('old_id', '=', part[12])])
        if part[12] not in old_list:
            property_account_payable_id = dict_account.get(part[32], False)
            property_account_receivable_id = dict_account.get(part[33], False)
            if not property_account_payable_id:
                property_account_payable_id = supplier[0]
            if not property_account_receivable_id:
                property_account_receivable_id = customer[0]
            accounts_data.append((part[12], property_account_payable_id, property_account_receivable_id))
            date_delivr = None
            if isinstance(part[17], (datetime, date)):
                date_delivr = part[17].isoformat()
            siret =None
            if part[29] != None:
                siret = part[29][:14]

            data = (part[0], part[1], part[2], part[3], part[4], part[5], part[6], part[7], part[8], part[9], part[10], part[11], part[12],
                    1 if part[13] else 0, 1 if part[14] else 0, part[15],part[16],date_delivr,part[18],part[19],
                    dict_state.get(part[20], None),part[21],part[22],part[23],part[24],part[25],part[26],part[27],part[28],siret,part[30])

            old_list.append(part[12])

            list_data.append(data)

    create_partners(list_data)
    if (i > 0):
        print(f"Number of records is:{i*2000}")

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

# print('old_list_ids',old_list_ids)

parents = []
partner_ids = odoo.env['res.partner'].search([('parent_id','!=', False)])
for p in get_partners(partner_ids):

    if p[31]!= None:
        data = (old_list_ids[p[31]], p[12])
        parents.append(data)
set_parents(parents)

# res_partner = odoov13.env['res.partner']
# partner_ids = res_partner.search([])
# partner_data = res_partner.read(partner_ids, ['old_id'])
# dict_part = {part['old_id']:part['id'] for part in partner_data}
#
# companies = get_companies()
# companies_list = []
#
# for p in companies:
#     if dict_part.get(p[1],False):
#         data = (p[0],dict_part.get(p[1],False)
#
#         )
#         companies_list.append(data)
# create_companies(companies_list)
