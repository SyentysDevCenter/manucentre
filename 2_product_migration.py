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

def get_product_product():
    try:
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)


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
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)


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
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

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
        connection = psycopg2.connect(user = USER_source,
                                      password = PASSWORD_source,
                                      host = HOST,
                                      port = Port_source,
                                      database = DB_souce)


        cursor = connection.cursor()
        query = """
                select t.id, t.categ_id, t.list_price, 
                        t.sale_ok, t.purchase_ok, t.uom_po_id, 
                        t.active,t.name, t.type, t.tracking,                         
                        t.product_brand_id, i.value, t.available_in_pos, t.to_weight
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
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

        cursor = connection.cursor()
        for p in products:
            cursor.execute("INSERT INTO product_template "
                           "(old_id, categ_id, list_price,"
                           "sale_ok, purchase_ok, uom_id,"
                           "uom_po_id, active, name, type,"
                           "tracking ,purchase_line_warn, sale_line_warn, product_brand_id,available_in_pos,"
                           "to_weight) "
                           "VALUES("
                           "%s, %s, %s,"
                           "%s, %s,%s,"
                           "%s, %s,%s, %s,"
                           "%s, %s,%s,%s,%s,%s)",
                           (p[0],p[1],p[2],
                            p[3],p[4],p[5],
                            p[6],p[7],p[8],p[9],
                            p[10],'','',p[11],p[12],p[13]),)

        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()


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
            # print('ffffffff', p[0], p[1])

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

def create_product_products(products):
    try:
        connection = psycopg2.connect(user = USER,
                                      password = PASSWORD,
                                      host = HOST,
                                      port = Port_dest,
                                      database = DB_dest)

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
            print('fffffff',p)
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

categ = odoov13.env['product.category']
categ_ids = categ.search([])
categ_data = categ.read(categ_ids, ['old_id'])
dict_categ= {part['old_id']:part['id'] for part in categ_data}

categ13_all = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['product', 'product_category_all'], {})
categ_all = odoo.execute_kw('ir.model.data', 'get_object_reference', ['product', 'product_category_all'], {})
categ.write([categ13_all[1]],{'old_id': categ_all[1]})
categ13_sale = odoov13.execute_kw('ir.model.data', 'get_object_reference', ['product', 'product_category_1'], {})
categ_sale = odoo.execute_kw('ir.model.data', 'get_object_reference', ['product', 'product_category_1'], {})
categ.write([categ13_sale[1]],{'old_id': categ_sale[1]})
#
# categs = get_product_categs()
# list_categs = []
# for p in categs:
#     if not p[0] in dict_categ:
#         data = (
#             p[0],p[1]
#         )
#         list_categs.append(data)
# create_product_category(list_categs, [])
# print('category done')
#
#
# parents =[]
# for p in categs:
#     if p[2] != None:
#         data = (dict_categ.get(p[2], None), p[0])
#         parents.append(data)
#
# create_product_category([], parents)
# odoov13.execute_kw('product.category', 'compute_complete_name', [categ_ids],{})
#
# print("categ parents done")



# uom_obj = odoov13.env['uom.uom']
# uom_ids = uom_obj.search([])
# uom_data = uom_obj.read(uom_ids, ['old_id'])
# dict_uom = {part['old_id']:part['id'] for part in uom_data}
#
#
# brand_obj = odoov13.env['product.brand']
# brand_ids = brand_obj.search([])
# brand_data = brand_obj.read(brand_ids, ['old_id'])
# dict_brand = {part['old_id']:part['id'] for part in brand_data}

# products = get_products()
# list_products = []
# for p in products:
#     name = p[7]
#     print('naaaaame', p[11], p[0])
#     if p[11] != None:
#         name= p[11]
#
#     data = (
#         p[0], dict_categ.get(p[1], None), p[2],
#         p[3], p[4], dict_uom.get(p[5], None),
#         dict_uom.get(p[5], None), p[6], name, p[8], p[9],
#         dict_brand.get(p[10], None),p[12],p[13]
#     )
#     list_products.append(data)
# create_products(list_products)

# print('product template done')
#


product_tmpl = odoov13.env['product.template']
product_tmpl_ids = product_tmpl.search(['|', ('active', '=', True),('active', '=', False)])
product_tmpl_data = product_tmpl.read(product_tmpl_ids, ['old_id'])
dict_product_tmpl = {part['old_id']:part['id'] for part in product_tmpl_data}

attribute_obj = odoov13.env['product.attribute']
product_attribute_ids = attribute_obj.search([])
product_attribute_data = attribute_obj.read(product_attribute_ids, ['old_id'])
dict_product_attribute = {part['old_id']:part['id'] for part in product_attribute_data}

# attribute_line = get_product_attribute_line()
# line_list = []
# for l in attribute_line:
#     data = (l[0], dict_product_tmpl.get(l[1],None), dict_product_attribute.get(l[2],None) )
#     print('daaaaaaaaata', data)
#     line_list.append(data)
# create_product_template_attribute_line(line_list)
# print("line d'attribut done")

attribute_val_obj = odoov13.env['product.attribute.value']
product_attribute_val_ids = attribute_val_obj.search([])
product_attribute_val_data = attribute_val_obj.read(product_attribute_val_ids, ['old_id'])
dict_product_attribute_val = {part['old_id']:part['id'] for part in product_attribute_val_data}

attribute_line_obj = odoov13.env['product.template.attribute.line']
product_attribute_line_ids = attribute_line_obj.search([])
product_attribute_line_data = attribute_line_obj.read(product_attribute_line_ids, ['old_id'])
dict_product_attribute_line = {part['old_id']:part['id'] for part in product_attribute_line_data}

# attribute_vals_m2m = get_product_attribute_line_vals_m2m()
# line_val_list = []
# for v in attribute_vals_m2m:
#     data =(dict_product_attribute_line.get(v[0], None),dict_product_attribute_val.get(v[1], None) )
#     line_val_list.append(data)
# create_product_attribute_line_vals_m2m(line_val_list)
# print("line d'attribut values done")

# product_products = get_product_product()
# list_p_p = []
# #
# # print(dict_product_tmpl.get(46,None))
# #
# for p in product_products:
#     if dict_product_tmpl.get(p[1],False):
#         data = (
#             p[0],
#             dict_product_tmpl.get(p[1],None),
#             p[2],
#             p[3],
#         )
#         list_p_p.append(data)
# create_product_products(list_p_p)
# #
product_prod = odoov13.env['product.product']
product_prod_ids = product_prod.search(['|', ('active', '=', True),('active', '=', False)])
product_prod_data = product_prod.read(product_prod_ids, ['old_id'])
dict_product_prod = {part['old_id']: part['id'] for part in product_prod_data}

product_vals = get_product_product_vals_m2m()
old_lines = []
prod_val_rel_data = []
for v in product_vals:
    ind = str(v[4])+'_'+str(v[0])
    # v.att_id, v.prod_id, p.product_tmpl_id, t.attribute_id, l.id:

    if ind not in old_lines:
        print('gggggggggggg', v[4], dict_product_attribute_line.get(v[4],None))
        data = (dict_product_attribute_val.get(v[0], None), dict_product_tmpl.get(v[2]),
                dict_product_attribute.get(v[3], None), dict_product_attribute_line.get(v[4],None))
        old_lines.append(ind)
        prod_val_rel_data.append(data)

create_product_template_attribute_value(prod_val_rel_data)
print('create_product_template_attribute_value done')
#
# product_template_att_value_obj = odoov13.env['product.template.attribute.value']
# product_template_att_value_ids = product_template_att_value_obj.search([])
# product_template_att_value_data = product_template_att_value_obj.read(product_template_att_value_ids,
#                                                                       ['attribute_line_id','product_attribute_value_id'])
# dict_product_template_att_value = {str(part['attribute_line_id'])+'_'+str(part['product_attribute_value_id']):part['id']
#                                    for part in product_template_att_value_data}
# print('dict_product_template_att_value', dict_product_template_att_value)
#
# product_vals_rel_data = []
# for v in product_vals:
#     line = dict_product_template_att_value.get(str(dict_product_attribute_line.get(v[4],None))+'_'+str(dict_product_attribute_val.get(v[0], None)),None)
#     data = (dict_product_prod.get(v[1], None), line)
#     product_vals_rel_data.append(data)
#
# create_product_attribute_rel(product_vals_rel_data)





