import odoorpc
import psycopg2
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

def get_product_brand():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)

        cursor = connection.cursor()
        query = """
                select id,name,partner_id,description
                from product_brand;
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

def get_product_tags():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)

        cursor = connection.cursor()
        query = """
                select id,name,parent_id,active
                from product_tag order by id;
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

def get_product_attributes():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)

        cursor = connection.cursor()
        query = """
                select id,name
                from product_attribute;
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

def get_product_attributes_values():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)

        cursor = connection.cursor()
        query = """
                select id, name, attribute_id
                from product_attribute_value;
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

def create_product_brands(brands):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in brands:
            cursor.execute("INSERT INTO product_brand (old_id,name,partner_id, description) VALUES(%s, %s,%s, %s)",
                           (p[0],p[1],p[2],p[3]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def create_product_attribute_value(value):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in value:
            cursor.execute("INSERT INTO product_attribute_value (old_id,name,attribute_id) VALUES(%s, %s,%s)",
                           (p[0],p[1],p[2]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def create_product_attribute(attribute):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in attribute:
            cursor.execute("INSERT INTO product_attribute (old_id,name,display_type, create_variant) "
                           "VALUES (%s, %s, 'select', 'dynamic')",
                           (p[0],p[1]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def create_product_tags(tags, parent={}):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        if not parent:
            for p in tags:
                cursor.execute("INSERT INTO product_tags (old_id,name,parent_id, active) VALUES(%s, %s,%s, %s)",
                               (p[0],p[1],p[2] or None,p[3]))
            connection.commit()
        if parent:
            for p in parent:
                cursor.execute("update product_tags set parent_id = %s where old_id = %s ",
                               (p[0], p[1]))
            connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()



# Login to source server
# odoo = odoorpc.ODOO('localhost', port=8091)
# odoo.login('manucentre9', 'admin', 'a')

# Login to destination server
odoov13 = odoorpc.ODOO(DEST_HOST, port=ODOO_DEST_PORT)
odoov13.login(DEST_DB, DEST_ODOO_USER, DEST_ODOO_PASSWORD)


partner = odoov13.env['res.partner']
partner_ids = partner.search([])
partner_data = partner.read(partner_ids, ['old_id'])
dict_partner= {part['old_id']:part['id'] for part in partner_data}


brands = get_product_brand()
list_brands = []
for p in brands:
    data = (
        p[0],p[1], dict_partner.get(p[2],None), p[3]
    )
    list_brands.append(data)
create_product_brands(list_brands)
print("Marque done")

attributes = get_product_attributes()
list_attributes = []
for p in attributes:
    data = (
        p[0],p[1]
    )
    list_attributes.append(data)
create_product_attribute(list_attributes)
print('Attribut done')

attribute_obj = odoov13.env['product.attribute']
attributes_ids = attribute_obj.search([])
att_data = attribute_obj.read(attributes_ids, ['old_id'])
dict_att= {part['old_id']:part['id'] for part in att_data}

values = get_product_attributes_values()
list_values = []
for p in values:
    if dict_att.get(p[2], False):
        data = (
            p[0],p[1], dict_att.get(p[2], False)
        )
    list_values.append(data)
create_product_attribute_value(list_values)
print("Valeur d'Attribut done")
#
tags = get_product_tags()
list_tags = []
for p in tags:

    data = (
        p[0],p[1],False, p[3]
    )
    list_tags.append(data)
create_product_tags(list_tags, {})
print("Tag done")

parents =[]
tag13 = odoov13.env['product.tags']
tags = get_product_tags()

tag13_ids = tag13.search([])
tag_data = tag13.read(tag13_ids, ['old_id'])
dict_tag= {part['old_id']:part['id'] for part in tag_data}
for p in tags:
    if p[2] != None:
        data = (dict_tag.get(p[2], False), p[0])
        parents.append(data)

create_product_tags([], parents)
print("Tag parents done")

