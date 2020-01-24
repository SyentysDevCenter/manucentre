import odoorpc
import psycopg2
USER = 'odoo13'
PASSWORD = 'odoo'
USER_source = 'openpg'
PASSWORD_source = 'openpgpwd'
HOST = "127.0.0.1"
Port_source = "5433"
Port_dest = "5432"
DB_souce = 'manucentre_last9'
DB_dest = 'manucentre1'

Companies_map = {1:1}

def get_accounts():
    try:
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)

        cursor = connection.cursor()
        query = f"select a.name,a.code,a.reconcile,a.user_type_id, at.name,a.id, a.company_id, tr.value " \
                f"from account_account a, account_account_type at, ir_translation tr " \
                f"where a.user_type_id=at.id and tr.res_id=at.id and " \
                f"tr.name='account.account.type,name' and tr.lang = 'fr_FR'" \
                ";"
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()
def get_account_types():
    try:
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

        cursor = connection.cursor()
        query = f"select at.name , at.id , at.name, tr.value " \
                f"from account_account_type at, ir_translation tr " \
                f"where tr.res_id=at.id and " \
                f"tr.name='account.account.type,name' and tr.lang = 'fr_FR';"
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()
def get_account_src_types():
    try:
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)

        cursor = connection.cursor()
        query = f"select at.name , at.id , at.name, tr.value " \
                f"from account_account_type at, ir_translation tr " \
                f"where tr.res_id=at.id and " \
                f"tr.name='account.account.type,name' and tr.lang = 'fr_FR';"
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def get_currents_accounts():
    try:
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

        cursor = connection.cursor()
        query = f"select a.name,a.code,a.reconcile,a.user_type_id,at.name,a.id, a.company_id, tr.value " \
                f"from account_account a, account_account_type at, ir_translation tr " \
                f"where a.user_type_id=at.id and tr.res_id=at.id and " \
                f"tr.name='account.account.type,name' and tr.lang = 'fr_FR';"
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def update_currents_accounts(accounts):
    try:
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

        cursor = connection.cursor()
        for c in accounts:
            cursor.execute(f"update account_account set old_id = %s , user_type_id = %s where id = %s;", (c[0], c[1], c[2]))
        connection.commit()

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

# Login to source server
odoo = odoorpc.ODOO('localhost', port=8091)
odoo.login('manucentre_last9', 'admin', 'a')

# Login to destination server
odoov13 = odoorpc.ODOO('localhost', port=8069)
odoov13.login('manucentre1', 'admin', 'a')


# account_type_ids  = odoo.env['account.account.type'].search([])
# # # # # # # at.name, at.id, tr.value
account_type_ids  =  get_account_types()
account_type_src_ids  =  get_account_src_types()
acc_dict = {}
acc_src_dict = {}
for acc_type in account_type_ids:
    acc_dict[acc_type[2]] = acc_type[1]
for acc_type in account_type_src_ids:
    acc_src_dict[acc_type[2]] = acc_type[1]

current_accounts = get_currents_accounts()
#
earing_type = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['account', 'data_unaffected_earnings'], {})
earing9_type = acc_src_dict.get("Bénéfices de l'année en cours", None)

current_dict = {}
earing_type_exist = False
for c in current_accounts :
    current_dict[c[1]] = c[5]
    if c[3] == earing_type[1]:
        earing_type_exist = c[5]
        print('fffffffff',earing_type_exist,earing_type  )
        update_currents_accounts([(None, acc_dict.get('Passif à court terme', None), c[5])])

print('current_dict', current_dict)

account_ids = get_accounts()
list_data = []
update_currents = []
for acc in account_ids:
    company = Companies_map.get(acc[6], False)
    if company != False:
        if not acc_dict.get(acc[4], False):
            type = acc_dict.get('Other Income', None)
        else:
            type = acc_dict.get(acc[4], None)
        print('acccccc', acc, acc_dict.get(acc[4], None))
        if acc[1] not in current_dict:
            list_data.append({
                            'name': acc[0],
                            'code': acc[1],
                            'reconcile' : acc[2],
                            'user_type_id': type,
                            'old_id': acc[5],
                            'company_id': company
                         })

        if acc[1] in current_dict :
            update_currents.append((acc[5], type, current_dict[acc[1]]))
        # if earing_type_exist and acc[3] == earing9_type:
        #     update_currents.append((acc[5], acc_dict.get(acc[4], None), earing_type_exist))

update_currents_accounts(update_currents)
result = odoov13.execute(
    'account.account', 'create',
    list_data)


