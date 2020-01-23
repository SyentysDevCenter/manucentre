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


def get_product_attribute_line():
    try:
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)


        cursor = connection.cursor()
        query = """
                select id, product_tmpl_id, attribute_id from product_attribute_line;
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

def get_product_attribute_line_vals_m2m():
    try:
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)


        cursor = connection.cursor()
        query = """
                select line_id, val_id from product_attribute_line_product_attribute_value_rel;
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
def get_product_product_vals_m2m():
    try:
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)


        cursor = connection.cursor()
        query = """
                select v.att_id, v.prod_id, p.product_tmpl_id , t.attribute_id, l.id
                 from product_attribute_value_product_product_rel v 
                 left join product_attribute_value t on t.id = v.att_id
                  left join product_product p on v.prod_id = p.id
                  LEFT JOIN product_attribute_line l on l.product_tmpl_id = p.product_tmpl_id and l.attribute_id = t.attribute_id
                 where p.active=True
                 order by p.product_tmpl_id;
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


def create_product_attribute_line_vals_m2m(vals):
    try:
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

        cursor = connection.cursor()
        for p in vals:

            cursor.execute("INSERT INTO product_attribute_value_product_template_attribute_line_rel "
                           "(product_template_attribute_line_id, product_attribute_value_id) "
                           "VALUES(%s, %s)",
                           (p[0], p[1]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def create_product_template_attribute_value(prod_val_rel_data):


    # v.att_id, v.prod_id, p.product_tmpl_id, t.attribute_id, l.id(products):
    try:
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

        cursor = connection.cursor()
        for p in prod_val_rel_data:
            cursor.execute("INSERT INTO product_template_attribute_value "
                           "(product_attribute_value_id, product_tmpl_id, attribute_id, attribute_line_id, ptav_active) "
                           "VALUES(%s, %s,%s, %s,True)",
                           (p[0], p[1], p[2], p[3]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()


def create_product_template_attribute_line(attributes):
    try:
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

        cursor = connection.cursor()
        for p in attributes:
            cursor.execute("INSERT INTO product_template_attribute_line "
                           "(old_id, product_tmpl_id, attribute_id, active) "
                           "VALUES(%s, %s,%s, True)",
                           (p[0], p[1], p[2]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def get_attribute_line_new():


    # v.att_id, v.prod_id, p.product_tmpl_id, t.attribute_id, l.id(products):
    try:
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

        cursor = connection.cursor()

        query ="""Select t.id, at.old_id as attr, te.old_id as temp, v.old_id as val
                        from product_template_attribute_line t
                       left join product_attribute_value_product_template_attribute_line_rel r 
                       on r.product_template_attribute_line_id = t.id
                       left join product_template te on te.id = t.product_tmpl_id
                       left join product_attribute at on at.id = t.attribute_id
                       left join product_attribute_value v on v.id = r.product_attribute_value_id  ;"""

        cursor.execute(query)
        record = cursor.fetchall()
        return record
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def create_product_attribute_rel(vals):


    # v.att_id, v.prod_id, p.product_tmpl_id, t.attribute_id, l.id(products):
    try:
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

        cursor = connection.cursor()
        for p in vals:
            cursor.execute("INSERT INTO product_variant_combination "
                           "(product_product_id, product_template_attribute_value_id) "
                           "VALUES(%s, %s)",
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
odoov13.login('manucentre1', 'admin', 'a')

product_tmpl = odoov13.env['product.template']
product_tmpl_ids = product_tmpl.search(['|', ('active', '=', True),('active', '=', False)])
product_tmpl_data = product_tmpl.read(product_tmpl_ids, ['old_id'])
dict_product_tmpl = {part['old_id']:part['id'] for part in product_tmpl_data}

attribute_obj = odoov13.env['product.attribute']
product_attribute_ids = attribute_obj.search([])
product_attribute_data = attribute_obj.read(product_attribute_ids, ['old_id'])
dict_product_attribute = {part['old_id']:part['id'] for part in product_attribute_data}

attribute_line = get_product_attribute_line()
line_list = []
for l in attribute_line:
    data = (l[0], dict_product_tmpl.get(l[1],None), dict_product_attribute.get(l[2],None) )
    line_list.append(data)
create_product_template_attribute_line(line_list)
print("line d'attribut done")

attribute_val_obj = odoov13.env['product.attribute.value']
product_attribute_val_ids = attribute_val_obj.search([])
product_attribute_val_data = attribute_val_obj.read(product_attribute_val_ids, ['old_id'])
dict_product_attribute_val = {part['old_id']:part['id'] for part in product_attribute_val_data}

attribute_line_obj = odoov13.env['product.template.attribute.line']
product_attribute_line_ids = attribute_line_obj.search([])
product_attribute_line_data = attribute_line_obj.read(product_attribute_line_ids, ['old_id'])
dict_product_attribute_line_1 = {part['old_id']:part['id'] for part in product_attribute_line_data}

attribute_vals_m2m = get_product_attribute_line_vals_m2m()
line_val_list = []
for v in attribute_vals_m2m:
    data =(dict_product_attribute_line_1.get(v[0], None),dict_product_attribute_val.get(v[1], None) )
    line_val_list.append(data)
create_product_attribute_line_vals_m2m(line_val_list)
print("line d'attribut values done")


product_prod = odoov13.env['product.product']
product_prod_ids = product_prod.search(['|', ('active', '=', True),('active', '=', False)])
product_prod_data = product_prod.read(product_prod_ids, ['old_id'])
dict_product_prod = {part['old_id']: part['id'] for part in product_prod_data}
#
product_vals = get_product_product_vals_m2m()
product_vals_err_data = []
old_er_line = []
for v in product_vals:
    if v[4] == None and (v[2], v[3]) not in old_er_line:
        product_vals_err_data.append((99999999, dict_product_tmpl.get(v[2], None),dict_product_attribute.get(v[3], None)))
        old_er_line.append((v[2], v[3]))
create_product_template_attribute_line(product_vals_err_data)
print('create_product_template_attribute_line err done')

attribute_line_obj = odoov13.env['product.template.attribute.line']
product_attribute_line_ids = attribute_line_obj.search([])
product_attribute_line_data = attribute_line_obj.read(product_attribute_line_ids, ['attribute_id', 'product_tmpl_id'])
dict_product_attribute_line = {str(part['product_tmpl_id'][0])+'_'+str(part['attribute_id'][0]):part['id'] for part in product_attribute_line_data}
err_val_data = []
old_val = []
for v in product_vals:
    if v[4] == None and (v[2], v[3]) not in old_val:
        line = dict_product_attribute_line.get(str(dict_product_tmpl.get(v[2], None))+'_'+str(dict_product_attribute.get(v[3], None)), None)

        err_val_data.append((line, dict_product_attribute_val.get(v[0], None)))
        old_val.append((v[2], v[3]))
create_product_attribute_line_vals_m2m(err_val_data)
print('create_product_template_attribute_line er done')



old_lines = []
prod_val_rel_data = []
for v in product_vals:
    line = dict_product_attribute_line.get(
        str(dict_product_tmpl.get(v[2], None)) + '_' + str(dict_product_attribute.get(v[3], None)),
        None)

    ind = str(str(line)+'_'+str(v[0]))
    # v.att_id, v.prod_id, p.product_tmpl_id, t.attribute_id, l.id:

    if ind not in old_lines:


        data = (dict_product_attribute_val.get(v[0], None), dict_product_tmpl.get(v[2], None),
                dict_product_attribute.get(v[3], None), line)
        old_lines.append(ind)
        prod_val_rel_data.append(data)

create_product_template_attribute_value(prod_val_rel_data)
print('create_product_template_attribute_value done')

product_template_att_value_obj = odoov13.env['product.template.attribute.value']
product_template_att_value_ids = product_template_att_value_obj.search([])
product_template_att_value_data = product_template_att_value_obj.read(product_template_att_value_ids,
                                                                      ['attribute_line_id','product_attribute_value_id'])
dict_product_template_att_value = {str(part['attribute_line_id'][0])+'_'+str(part['product_attribute_value_id'][0]):part['id']
                                   for part in product_template_att_value_data}
line_dict = {}
lines = get_attribute_line_new()
for line in lines:
    line_dict[str(line[1])+'_'+str(line[2])+'_'+str(line[3])]= line[0]


product_vals_rel_data = []
done_old = []
for v in product_vals:
    att_line = line_dict.get(str(v[3])+'_'+str(v[2]) + '_' + str(v[0]),None)
    line = dict_product_template_att_value.get(str(att_line)+'_'+str(dict_product_attribute_val.get(v[0], None)),None)
    if line:
        data = (dict_product_prod.get(v[1], None), line)
        if data not in product_vals_rel_data:
            product_vals_rel_data.append(data)
        else:
            done_old.append(data)

print('done repeat', done_old)
create_product_attribute_rel(product_vals_rel_data)
print('create_product_attribute_rel done')
for line in done_old:
    product_prod.write([line[0]], {'probleme': str(line)})





