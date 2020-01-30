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


def get_product_product():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)

        cursor = connection.cursor()
        query = """
                select id,product_tmpl_id,default_code,active
                from product_product;
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

def get_product_categs():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)


        cursor = connection.cursor()
        query = """
                select id, name, parent_id
                from product_category;
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

def create_product_category(categs, parent):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        if not parent:
            for p in categs:
                cursor.execute("INSERT INTO product_category "
                               "(old_id, name) "
                               "VALUES(%s, %s)",
                               (p[0], p[1]))
            connection.commit()
        if parent:
            for p in parent:
                cursor.execute("update product_category set parent_id = %s where old_id = %s ",
                               (p[0], p[1]))
            connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def get_products():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)


        cursor = connection.cursor()
        query = """
                select t.id, t.categ_id, t.list_price, 
                        t.sale_ok, t.purchase_ok, t.uom_po_id, 
                        t.active,t.name, t.type, t.tracking,                         
                        t.product_brand_id, i.value, t.available_in_pos, t.to_weight, t.sale_line_warn_msg, 
                        t.purchase_line_warn_msg, t.purchase_method
                        from product_template t left join ir_translation i on t.id = i.res_id
                        and i.name='product.template,name' and lang ='fr_FR';
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

def create_products(products):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in products:
            cursor.execute("INSERT INTO product_template "
                           "(old_id, categ_id, list_price,"
                           "sale_ok, purchase_ok, uom_id,"
                           "uom_po_id, active, name, type,"
                           "tracking, purchase_line_warn, sale_line_warn, product_brand_id,"
                           "available_in_pos, to_weight, sale_line_warn_msg,"
                           "purchase_line_warn_msg, invoice_policy, purchase_method) "
                           "VALUES("
                           "%s, %s, %s,"
                           "%s, %s, %s,"
                           " %s, %s, %s, %s, "
                           " %s, 'no-message','no-message', %s,"
                           "%s, %s, %s, "
                           "%s, %s, %s)",
                           (p[0], p[1], p[2],
                            p[3], p[4], p[5],
                            p[6], p[7], p[8], p[9],
                            p[10], p[11],
                            p[12], p[13], p[14],
                            p[15], 'order', p[16]),)

        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def create_product_products(products):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in products:
            cursor.execute("INSERT INTO product_product "
                           "(old_id, product_tmpl_id, default_code, active) "
                           "VALUES(%s, %s,%s, %s)",
                           (p[0], p[1], p[2], p[3]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()


# Login to source server
odoo = odoorpc.ODOO(SOURCE_HOST, port=ODOO_SOURCE_PORT)
odoo.login(SOURCE_DB,SOURCE_ODOO_USER, SOURCE_ODOO_PASSWORD)

# Login to destination server
odoov13 = odoorpc.ODOO(DEST_HOST, port=ODOO_DEST_PORT)
odoov13.login(DEST_DB, DEST_ODOO_USER, DEST_ODOO_PASSWORD)


categ = odoov13.env['product.category']
categ13_all = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['product', 'product_category_all'], {})
categ_all = odoo.execute_kw('ir.model.data', 'get_object_reference', ['product', 'product_category_all'], {})
categ.write([categ13_all[1]],{'old_id': categ_all[1]})
categ13_sale = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['product', 'product_category_1'], {})
categ_sale = odoo.execute_kw('ir.model.data', 'get_object_reference', ['product', 'product_category_1'], {})
categ.write([categ13_sale[1]],{'old_id': categ_sale[1]})

categs = get_product_categs()
list_categs = []
for p in categs:
    if not p[0] in list_categs:
        data = (
            p[0],p[1]
        )
        list_categs.append(data)
create_product_category(list_categs, [])
print('category done')

categ_ids = categ.search([])
categ_data = categ.read(categ_ids, ['old_id'])
dict_categ= {part['old_id']:part['id'] for part in categ_data}

parents =[]
for p in categs:
    if p[2] != None:
        data = (dict_categ.get(p[2], None), p[0])
        parents.append(data)

create_product_category([], parents)
odoov13.execute_kw('product.category', 'compute_complete_name', [categ_ids],{})

print("categ parents done")



uom_obj = odoov13.env['uom.uom']
uom_ids = uom_obj.search([])
uom_data = uom_obj.read(uom_ids, ['old_id'])
dict_uom = {part['old_id']:part['id'] for part in uom_data}


brand_obj = odoov13.env['product.brand']
brand_ids = brand_obj.search([])
brand_data = brand_obj.read(brand_ids, ['old_id'])
dict_brand = {part['old_id']:part['id'] for part in brand_data}

products = get_products()
list_products = []
for p in products:
    name = p[7]
    if p[11] != None:
        name= p[11]

    data = (
    p[0], dict_categ.get(p[1], None), p[2],
    p[3], p[4], dict_uom.get(p[5], None),
    dict_uom.get(p[5], None), p[6], name, p[8],
    p[9], dict_brand.get(p[10], None),
    p[12],p[13],p[14],
    p[15],p[15]
    )
    list_products.append(data)
create_products(list_products)

print('product template done')



product_tmpl = odoov13.env['product.template']
product_tmpl_ids = product_tmpl.search(['|', ('active', '=', True),('active', '=', False)])
product_tmpl_data = product_tmpl.read(product_tmpl_ids, ['old_id'])
dict_product_tmpl = {part['old_id']:part['id'] for part in product_tmpl_data}


product_products = get_product_product()
list_p_p = []

for p in product_products:
    if dict_product_tmpl.get(p[1],False):
        data = (
            p[0],
            dict_product_tmpl.get(p[1],None),
            p[2],
            p[3],
        )
        list_p_p.append(data)
create_product_products(list_p_p)
