import odoorpc
import psycopg2
import odoorpc
import psycopg2

def get_prices():
    try:
        connection = psycopg2.connect(user = "odoo",
                                      password = "odoo",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "APOL_test")

        cursor = connection.cursor()
        query = """
                select name,product_tmpl_id,delay,sequence,company_id,product_name,currency_id,min_qty,product_code,
                price,mult_qty,mult_price
                from product_supplierinfo;
                """
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def create_prices(prices):
    try:
        connection = psycopg2.connect(user = "odoo",
                                      password = "odoo",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "APOL_ERP")

        cursor = connection.cursor()
        for p in prices:
            cursor.execute("INSERT INTO product_supplierinfo (name,product_tmpl_id,delay,sequence,company_id,product_name,currency_id,min_qty,product_code,price,mult_qty,mult_price)"
                           "VALUES(%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s)",
                           (p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10],p[11]))
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
        connection = psycopg2.connect(user = "odoo",
                                      password = "odoo",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "APOL_test")

        cursor = connection.cursor()
        print(tuple(partner_ids,))
        query = f"select p.name,p.is_company,p.ref,p.street,p.street2,p.zip,p.city,p.function,p.phone,p.mobile,p.fax,p.email,p.id," \
                f"CAST(SPLIT_PART(ir.value_reference,',',2) as INTEGER),CAST(SPLIT_PART(ir2.value_reference,',',2) as INTEGER)," \
                f"p.customer,p.supplier,p.active from res_partner p LEFT OUTER JOIN ir_property ir ON p.ID = CAST(SPLIT_PART(ir.res_id,',',2) as INTEGER)" \
                f" and ir.name ='property_account_payable_id' LEFT OUTER JOIN ir_property ir2 ON p.ID = CAST(SPLIT_PART(ir2.res_id,',',2) as INTEGER) " \
                f" and ir2.name ='property_account_receivable_id' where p.id in {tuple(partner_ids)}"
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
odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('APOL_test', 'admin', 'a')

# Login to destination server
odoov13 = odoorpc.ODOO('localhost', port=8060)
odoov13.login('APOL_ERP', 'admin', 'a')


payment_term = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['account', 'account_payment_term_30days'], {})

account = odoov13.env['account.account']

customer = account.search([('code','=','411100')],limit=1)
if not customer:
    raise Exception('No customer account is defined!')
supplier = account.search([('code','=','401100')],limit=1)
if not supplier:
    raise Exception('No supplier account is defined!')
print("customer,supplier",customer,supplier)


partner = odoo.env['res.partner']

offset = 0

for i in range(160):
    partner_ids = partner.search([], offset=offset, limit=100)
    offset += 100
    print(len(partner_ids))
    list_data = []
    for part in get_partners(partner_ids):
        property_account_payable_id = supplier[0]
        property_account_receivable_id = customer[0]
        data = {
                'name': part[0],
                'is_company':part[1],
                'ref': part[2],
                'street': part[3],
                'street2': part[4],
                'zip': part[5],
                'city':part[6],
                'function':part[7],
                'phone':part[8],
                'mobile':part[9],
                #'fax':part[10],
                'email':part[11],
                'old_id': part[12],
                'property_payment_term_id': payment_term[1],
                'property_supplier_payment_term_id': payment_term[1],
                'property_account_payable_id': property_account_payable_id,
                'property_account_receivable_id' : property_account_receivable_id,
                'customer_rank' : 1 if part[15] else 0,
                'supplier_rank' : 1 if part[16] else 0,
                'active' : part[17],
            }
        list_data.append(data)
    result = odoov13.execute(
        'res.partner', 'create',
        list_data)
    if (i > 0):
        print(f"Number of records is:{i*100}")

product_tmpl = odoov13.env['product.template']
product_tmpl_ids = product_tmpl.search([])
product_tmpl_data = product_tmpl.read(product_tmpl_ids, ['old_id'])
dict_product_tmpl = {part['old_id']:part['id'] for part in product_tmpl_data}

res_partner = odoov13.env['res.partner']
partner_ids = res_partner.search([])
partner_data = res_partner.read(partner_ids, ['old_id'])
dict_part = {part['old_id']:part['id'] for part in partner_data}

prices = get_prices()
list_p_p = []

for p in prices:
    if dict_part.get(p[0],False) and dict_product_tmpl.get(p[1],False):
        data = (
            dict_part.get(p[0],False),
            dict_product_tmpl.get(p[1],None),
            p[2],
            p[3],
            p[4],
            p[5],
            p[6],
            p[7],
            p[8],
            p[9],
            p[10],
            p[11],
        )
        list_p_p.append(data)
create_prices(list_p_p)

