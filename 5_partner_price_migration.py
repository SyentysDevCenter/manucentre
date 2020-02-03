import odoorpc
import psycopg2
import databaseconfig as cfg

# SOURCE
SOURCE_HOST =cfg.source_connect['SOURCE_HOST']
SOURCE_USER =cfg.source_connect['SOURCE_USER']
SOURCE_PASSWORD = cfg.source_connect['SOURCE_PASSWORD']
SOURCE_PORT = cfg.source_connect['SOURCE_PORT']
SOURCE_DB = cfg.source_connect['SOURCE_DB']
SOURCE_ODOO_USER = cfg.source_connect['SOURCE_ODOO_USER']
SOURCE_ODOO_PASSWORD = cfg.source_connect['SOURCE_ODOO_PASSWORD']
ODOO_SOURCE_PORT = cfg.source_connect['ODOO_SOURCE_PORT']

# DEST
DEST_ODOO_USER =cfg.dest_connect['DEST_ODOO_USER']
DEST_ODOO_PASSWORD = cfg.dest_connect['DEST_ODOO_PASSWORD']
DEST_USER = cfg.dest_connect['DEST_USER']
DEST_PASSWORD = cfg.dest_connect['DEST_PASSWORD']
DEST_DB = cfg.dest_connect['DEST_DB']
DEST_HOST = cfg.dest_connect['DEST_HOST']
DEST_PORT = cfg.dest_connect['DEST_PORT']
ODOO_DEST_PORT = cfg.dest_connect['ODOO_DEST_PORT']


Companies_map = cfg.company_map


def get_product_tags():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)


        cursor = connection.cursor()
        query = """
                select tag_id, product_id
                from product_product_tag_rel;
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



def get_purchase_price():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)


        cursor = connection.cursor()
        query = """
                select l.price_unit ,l.product_id, o.company_id from purchase_order_line l 
                left join purchase_order o on l.order_id = o.id
                group by o.company_id, l.product_id, l.price_unit
                order by max(o.date_order) desc, l.product_id, o.company_id;
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

def update_standard_price(price):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()

        for p in price:
            cursor.execute("INSERT INTO ir_property "
                           "(name, res_id, company_id,"
                           " fields_id, value_float, type) "
                           "VALUES(%s, %s, %s,"
                           " %s, %s, %s)",
                           (p[0], p[1], p[2], p[3], p[4], p[5]))
        connection.commit()

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()


def create_product_tags(tags):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()

        for p in tags:
            cursor.execute("INSERT INTO product_tmpl_tags_rel "
                           "(tag_id, product_tmpl_id) "
                           "VALUES(%s, %s)",
                           (p[0], p[1]))
        connection.commit()

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()



def get_prices():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)

        cursor = connection.cursor()
        query = """
                select name, product_tmpl_id, delay, sequence, product_name,
                       currency_id, min_qty, product_code, price, product_id, date_start, date_end, id
                       
                from product_supplierinfo WHERE name != 1 and company_id=1;
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
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in prices:
            cursor.execute("INSERT INTO product_supplierinfo "
                           "(name, product_tmpl_id, delay, sequence, company_id,"
                           "product_name, currency_id, min_qty, product_code, price, product_id, date_start, date_end, old_id"
                           ") "
                           "VALUES(%s, %s, %s, %s, %s,"
                           "     %s, %s, %s, %s, %s, "
                           "%s, %s, %s, %s"
                           " )",
                           (p[0], p[1], p[2], p[3], 1,
                            p[4], p[5], p[6], p[7], p[8], p[9],
                            p[10], p[11], p[12]
                           ))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

# Login to source server
#odoo = odoorpc.ODOO(SOURCE_HOST, port=ODOO_SOURCE_PORT)
#odoo.login(SOURCE_DB,SOURCE_ODOO_USER, SOURCE_ODOO_PASSWORD)

# Login to destination server
odoov13 = odoorpc.ODOO(DEST_HOST, port=ODOO_DEST_PORT)
odoov13.login(DEST_DB, DEST_ODOO_USER, DEST_ODOO_PASSWORD)

#partner = odoo.env['res.partner']

product_tmpl = odoov13.env['product.template']
product_tmpl_ids = product_tmpl.search([])
product_tmpl_data = product_tmpl.read(product_tmpl_ids, ['old_id'])
dict_product_tmpl = {part['old_id']:part['id'] for part in product_tmpl_data}

res_partner = odoov13.env['res.partner']
partner_ids = res_partner.search([])
partner_data = res_partner.read(partner_ids, ['old_id'])
dict_part = {part['old_id']:part['id'] for part in partner_data}

product_prod = odoov13.env['product.product']
product_prod_ids = product_prod.search(['|', ('active', '=', True),('active', '=', False)])
product_prod_data = product_prod.read(product_prod_ids, ['old_id'])
dict_product_prod = {part['old_id']: part['id'] for part in product_prod_data}

prices = get_prices()
list_p_p = []
for p in prices:
    if dict_part.get(p[0],False) and dict_product_tmpl.get(p[1],False):
        data = (
            dict_part.get(p[0],False), dict_product_tmpl.get(p[1],None), p[2], p[3],
            p[4], p[5], p[6], p[7], p[8],dict_product_prod.get(p[9], None)
            , p[10], p[11], p[12]

        )
        list_p_p.append(data)
create_prices(list_p_p)

print('prices done')



product_tags = get_product_tags()
tags_produ_list = []
for p in product_tags:
    if dict_product_tmpl.get(p[1],False):
        data = (
            p[0],
            dict_product_tmpl.get(p[1], None),

        )

        tags_produ_list.append(data)

create_product_tags(tags_produ_list)

print("tags done")

prices = get_purchase_price()
# # # # # # l.price_unit ,l.product_id, o.company_id , max(o.date_order)
product_price = []
standard_price_field = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['product', 'field_product_product__standard_price'], {})
prod = []
for p in prices:
    company = Companies_map.get(p[2], False)
    if company != False:
        if p[1] not in prod:
            product_id = dict_product_prod.get(p[1], False)
            if product_id:
                product_price.append(('standard_price', 'product.product,'+str(product_id), company,standard_price_field[1],float(p[0]) ,'float' ))
update_standard_price(product_price)
print('prix standard done')
# # # # # # #(name, res_id, company_id, fields_id, value_float, type)