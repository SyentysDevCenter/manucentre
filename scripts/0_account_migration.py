import odoorpc
import psycopg2

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

#Company_mapping
company_map = {
    '1':'1',
    '22':'13',
    '24':'11',
    '25':'12',
    '26':'13',
}

#Account config
account_code_length = 7

def update_account_code_length():
    odoov13 = odoorpc.ODOO(DEST_HOST, port=8069)
    odoov13.login(DEST_DB, DEST_ODOO_USER, DEST_ODOO_PASSWORD)

    account_ids = odoov13.env['account.account'].search([])
    for acc in odoov13.env['account.account'].browse(account_ids):
        acc.code = acc.code.ljust(account_code_length, '0')

def get_accounts():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)
        cursor = connection.cursor()
        query = f"select a.id,a.company_id,a.code,a.name,a.user_type_id,a.reconcile,at.name, tr.value " \
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
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

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
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)

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
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        query = f"select a.id,a.company_id,a.code,a.name,a.reconcile,a.user_type_id,at.name, tr.value " \
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

def update_currents_accounts(account_id,old_id):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        cursor.execute(f"update account_account set old_id = %s where id = %s;", (old_id,account_id))
        connection.commit()

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

# Login to destination server
odoov13 = odoorpc.ODOO(DEST_HOST, port=8069)
odoov13.login(DEST_DB, DEST_ODOO_USER, DEST_ODOO_PASSWORD)

account_type_ids  =  get_account_types()
account_type_src_ids  =  get_account_src_types()
acc_dict = {}
acc_src_dict = {}
for acc_type in account_type_ids:
    acc_dict[acc_type[2]] = acc_type[1]
for acc_type in account_type_src_ids:
    acc_src_dict[acc_type[2]] = acc_type[1]

type_mapping = {}
for src_type in acc_src_dict:
    if acc_dict.get(src_type,False):
        type_mapping[acc_src_dict[src_type]]=acc_dict.get(src_type,False)
    else:
        if src_type == 'Direct Costs':
            type_mapping[acc_src_dict[src_type]] = acc_dict.get('Expenses', False)

account_ids = get_accounts()
current_accounts = get_currents_accounts()

current_account_dict = {}
for account in current_accounts:
    current_account_dict[','.join([account[2],str(account[1])])]=account[0]

list_data = []
to_create = {}
for src_account in account_ids:
    if str(src_account[1]) in company_map.keys():
        comany = company_map[str(src_account[1])]
        code_comapny = ','.join([src_account[2],comany])
        if current_account_dict.get(code_comapny,False):
            update_currents_accounts(current_account_dict[code_comapny],src_account[0])
        else:
            if not to_create.get(code_comapny,False):
                to_create[code_comapny]=True
                list_data.append({
                    'name': src_account[3],
                    'code': src_account[2],
                    'reconcile': src_account[5],
                    'user_type_id': type_mapping[src_account[4]],
                    'company_id':int(comany),
                    'old_id': src_account[0],
                })

result = odoov13.execute(
    'account.account', 'create',
    list_data)