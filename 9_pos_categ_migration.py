import odoorpc
import psycopg2
import databaseconfig as cfg

# SOURCE
SOURCE_HOST = cfg.source_connect['SOURCE_HOST']
SOURCE_USER = cfg.source_connect['SOURCE_USER']
SOURCE_PASSWORD = cfg.source_connect['SOURCE_PASSWORD']
SOURCE_PORT = cfg.source_connect['SOURCE_PORT']
SOURCE_DB = cfg.source_connect['SOURCE_DB']
SOURCE_ODOO_USER = cfg.source_connect['SOURCE_ODOO_USER']
SOURCE_ODOO_PASSWORD = cfg.source_connect['SOURCE_ODOO_PASSWORD']
ODOO_SOURCE_PORT = cfg.source_connect['ODOO_SOURCE_PORT']

# DEST
DEST_ODOO_USER = cfg.dest_connect['DEST_ODOO_USER']
DEST_ODOO_PASSWORD = cfg.dest_connect['DEST_ODOO_PASSWORD']
DEST_USER = cfg.dest_connect['DEST_USER']
DEST_PASSWORD = cfg.dest_connect['DEST_PASSWORD']
DEST_DB = cfg.dest_connect['DEST_DB']
DEST_HOST = cfg.dest_connect['DEST_HOST']
DEST_PORT = cfg.dest_connect['DEST_PORT']
ODOO_DEST_PORT = cfg.dest_connect['ODOO_DEST_PORT']

Companies_map = cfg.company_map

def get_product_pos_categ():
    try:
        connection = psycopg2.connect(user=SOURCE_USER,
                                      password=SOURCE_PASSWORD,
                                      host=SOURCE_HOST,
                                      port=SOURCE_PORT,
                                      database=SOURCE_DB)

        cursor = connection.cursor()
        query = """
                select distinct pp.id as product_id,cat.id as cat_id
                from pos_template pt, product_product pr, pos_category cat,product_template pp
                where pr.id = pt.pos_category_id and cat.id = pt.tempcat
                and pp.id = pr.product_tmpl_id;
                """
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

def get_pos_categ():
    try:
        connection = psycopg2.connect(user=SOURCE_USER,
                                      password=SOURCE_PASSWORD,
                                      host=SOURCE_HOST,
                                      port=SOURCE_PORT,
                                      database=SOURCE_DB)

        cursor = connection.cursor()
        query = """
                select id,name,parent_id from pos_category;
                """
        cursor.execute(query)
        record = cursor.fetchall()
        return record

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

def update_categ_parent(parent):
    try:
        connection = psycopg2.connect(user=DEST_USER,
                                      password=DEST_PASSWORD,
                                      host=DEST_HOST,
                                      port=DEST_PORT,
                                      database=DEST_DB)

        cursor = connection.cursor()
        for p in parent:
            cursor.execute("update pos_category set parent_id = %s where old_id = %s ",
                           (p[0], p[1]))
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

def create_pos_categ(cats):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for cat in cats:
            cursor.execute("INSERT INTO pos_category "\
             "(old_id,name)"\
             " VALUES(%s,%s)",
                           (cat[0],cat[1]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def create_pos_product_cat(cats):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for cat in cats:
            cursor.execute("update product_template set pos_categ_id = %s where id = %s",(cat[0],cat[1]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

# Login to destination server
odoov13 = odoorpc.ODOO(DEST_HOST, port=ODOO_DEST_PORT)
odoov13.login(DEST_DB, DEST_ODOO_USER, DEST_ODOO_PASSWORD)


old_pos_categ = get_pos_categ()
pos_categs = []
for cat in old_pos_categ:
    pos_categs.append(
        [cat[0],cat[1]]
    )
create_pos_categ(pos_categs)

pos_categ = odoov13.env['pos.category']
categ_ids = pos_categ.search([])
categ_data = pos_categ.read(categ_ids, ['old_id'])
dict_categ= {part['old_id']:part['id'] for part in categ_data}

product_prod = odoov13.env['product.template']
product_prod_ids = product_prod.search(['|', ('active', '=', True), ('active', '=', False)])
product_prod_data = product_prod.read(product_prod_ids, ['old_id'])
dict_product_prod = {part['old_id']: part['id'] for part in product_prod_data}

parents =[]
for p in old_pos_categ:
    if p[2] != None:
        data = (dict_categ.get(p[2], None), p[0])
        parents.append(data)
update_categ_parent(parents)

product_categ_id = get_product_pos_categ()

product_pos_cat = []
for p_cat in product_categ_id:
    if dict_categ.get(p_cat[1],False) and dict_product_prod.get(p_cat[0],False):
        product_pos_cat.append([dict_categ.get(p_cat[1],False), dict_product_prod.get(p_cat[0],False)])
create_pos_product_cat(product_pos_cat)

print('Pos categ done')
