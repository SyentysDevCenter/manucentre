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
DB_dest = 'manucentre2'

def get_product_brand():
    try:
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)

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
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)

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
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)

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
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)

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
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

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
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

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
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

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
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

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
odoo = odoorpc.ODOO('localhost', port=8091)
odoo.login('manucentre_last9', 'admin', 'a')

# Login to destination server
odoov13 = odoorpc.ODOO('localhost', port=8069)
odoov13.login('manucentre2', 'admin', 'a')


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

