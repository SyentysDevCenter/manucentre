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


def get_product_attribute_line():
    try:
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)


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
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)


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
        connection = psycopg2.connect(user = SOURCE_USER,
                                      password = SOURCE_PASSWORD,
                                      host = SOURCE_HOST,
                                      port = SOURCE_PORT,
                                      database = SOURCE_DB)


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
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

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

def update_product_probleme(vals):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in vals:

            cursor.execute("""Update product_product set probleme = %s where id = %s""",
                           (p[0], p[1]))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()
def update_probleme_variante_tmpl(vals):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in vals:

            cursor.execute("""Update product_template set probleme_variante = True where id = %s""",
                           (p,))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def update_archive_product(vals):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in vals:
            cursor.execute("""Update product_product set active = False where id = %s""",
                           (p,))
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
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

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
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

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
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

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

def get_m2m_line_val_comb():


    #  #  #  # v.att_id, v.prod_id, p.product_tmpl_id, t.attribute_id, l.id(products):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()

        #  #  #  # line_id  val_id  tmpl_old at_old val_old line_old
        query ="""Select r.product_template_attribute_line_id, r.product_attribute_value_id, 
                    te.old_id as tmpl, at.old_id, v.old_id, t.old_id
                        from product_attribute_value_product_template_attribute_line_rel r 
                       left join product_template_attribute_line t on r.product_template_attribute_line_id = t.id
                       left join product_template te on te.id = t.product_tmpl_id
                       left join product_attribute at on at.id = t.attribute_id
                       left join product_attribute_value v on v.id = r.product_attribute_value_id 
                        ;"""

        cursor.execute(query)
        record = cursor.fetchall()
        return record
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def get_product_template_att_value():
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)
        cursor = connection.cursor()
        query ="""Select r.id , r.attribute_line_id, r.product_attribute_value_id                 
                        from product_template_attribute_value r                         
                        ;"""

        cursor.execute(query)
        record = cursor.fetchall()
        return record
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()

def get_product_template_att_lines():
    # product_attribute_line_data = attribute_line_obj.read(product_attribute_line_ids,
    #                                                       ['attribute_id', 'product_tmpl_id'])
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()

        query ="""Select r.id , r.attribute_id, r.product_tmpl_id
                 
                        from product_template_attribute_line r 
                        
                        ;"""

        cursor.execute(query)
        record = cursor.fetchall()
        return record
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
            if(connection):
                cursor.close()
                connection.close()


def get_product_product_combination():

    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()

        query = """select distinct p.product_product_id, pa.product_tmpl_id, ARRAY (select pp.product_template_attribute_value_id
					   from product_variant_combination pp where p.product_product_id = pp.product_product_id)
					   from  product_variant_combination p 
					   left join product_product pa on p.product_product_id = pa.id 
					   group by p.product_product_id, pa.product_tmpl_id
					   order by  pa.product_tmpl_id

                        ;"""

        cursor.execute(query)
        record = cursor.fetchall()
        return record
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()


def update_product_combination_indices(vals):


    # v.att_id, v.prod_id, p.product_tmpl_id, t.attribute_id, l.id(products):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for p in vals:
            cursor.execute("UPDATE product_product set combination_indices= %s where id = %s",
                           (p[0], p[1]))
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
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

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
#odoo = odoorpc.ODOO(SOURCE_HOST, port=ODOO_SOURCE_PORT)
#odoo.login(SOURCE_DB,SOURCE_ODOO_USER, SOURCE_ODOO_PASSWORD)

# Login to destination server
odoov13 = odoorpc.ODOO(DEST_HOST, port=ODOO_DEST_PORT)
odoov13.login(DEST_DB, DEST_ODOO_USER, DEST_ODOO_PASSWORD)

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
    if dict_product_tmpl.get(l[1], False):
        data = (l[0], dict_product_tmpl.get(l[1], None), dict_product_attribute.get(l[2], None))
        line_list.append(data)
create_product_template_attribute_line(line_list)
print("line d'attribut done")

attribute_val_obj = odoov13.env['product.attribute.value']
product_attribute_val_ids = attribute_val_obj.search([])
product_attribute_val_data = attribute_val_obj.read(product_attribute_val_ids, ['old_id'])
dict_product_attribute_val = {part['old_id']: part['id'] for part in product_attribute_val_data}

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
    #     #    #    #  Pour generer les ligne d'attribut manquante pour des variante sans ligne d'origine
    if v[4] == None and (v[2], v[3]) not in old_er_line:
        product_vals_err_data.append((99999999, dict_product_tmpl.get(v[2], None),dict_product_attribute.get(v[3], None)))
        old_er_line.append((v[2], v[3]))
create_product_template_attribute_line(product_vals_err_data)
print('create_product_template_attribute_line err done')

attribute_line_obj = odoov13.env['product.template.attribute.line']
# product_attribute_line_ids = attribute_line_obj.search([])
product_attribute_line_data = get_product_template_att_lines()
# product_attribute_line_data = attribute_line_obj.read(product_attribute_line_ids, ['attribute_id', 'product_tmpl_id'])
dict_product_attribute_line = {str(part[2])+'_'+str(part[1]):part[0] for part in product_attribute_line_data}

m2m_lin_val = get_m2m_line_val_comb()
m2m_lin_list = []
old_val = []
old_val_val = []
for l in m2m_lin_val:
    #     #    #    #(old_line,old_val)
    #  #  #  # line_id  val_id  tmpl_old at_old val_old line_old
    m2m_lin_list.append((l[5], l[4]))
    old_val_val.append((l[2], l[3], l[4] ))
err_val_data = []

for v in product_vals:
    #     #    #    #    val, prod, tmpl, attr, line
    #     #    #    # pour ajouter les valeur d'attribut au ligne correspondant à des variante sans ligne d'origine
        if v[4] == None  and (v[2], v[3]) not in old_val or (v[2], v[3], v[0]) not in old_val_val:
            line = dict_product_attribute_line.get(str(dict_product_tmpl.get(v[2], None))+'_'+str(dict_product_attribute.get(v[3], None)), None)

            err_val_data.append((line, dict_product_attribute_val.get(v[0], None)))
            old_val_val.append((v[2], v[3], v[0]))
            old_val.append((v[2], v[3]))

    #     #    #    #  Pour generer des valeur d'attribut au ligne pour des variantes ayant des valeur non lié à la bonne ligne d'attribut
        if v[4] != None and (v[4], v[0]) not in m2m_lin_list and (v[2], v[3], v[0]) not in old_val_val:
            line = dict_product_attribute_line.get(
                str(dict_product_tmpl.get(v[2], None)) + '_' + str(dict_product_attribute.get(v[3], None)), None)

            err_val_data.append((line, dict_product_attribute_val.get(v[0], None)))
            old_val.append((v[2], v[3]))
            old_val_val.append((v[2], v[3], v[0]))
            m2m_lin_list.append((v[4], v[0]))
create_product_attribute_line_vals_m2m(err_val_data)
print('create_product_attribute_line_vals_m2m er done')



old_lines = []
prod_val_rel_data = []
for v in product_vals:
    #     #    #    #  pour remplir la table product_template_attribute_value
    line = dict_product_attribute_line.get(
        str(dict_product_tmpl.get(v[2], None)) + '_' + str(dict_product_attribute.get(v[3], None)),
        None)

    ind = str(str(line)+'_'+str(v[0]))
    if ind not in old_lines:
        data = (dict_product_attribute_val.get(v[0], None), dict_product_tmpl.get(v[2], None),
                dict_product_attribute.get(v[3], None), line)
        old_lines.append(ind)
        prod_val_rel_data.append(data)

create_product_template_attribute_value(prod_val_rel_data)
print('create_product_template_attribute_value done')


product_template_att_value_data = get_product_template_att_value()
dict_product_template_att_value = {str(part[1])+'_'+str(part[2]):part[0]
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
        if data in product_vals_rel_data:
            done_old.append(data)
        if data not in product_vals_rel_data:
            product_vals_rel_data.append(data)



print('done repeat', done_old)
create_product_attribute_rel(product_vals_rel_data)
print('create_product_attribute_rel done')
probleme_data = []
for line in done_old:
    date = (line[0], str(line))
    probleme_data.append(data)

update_product_probleme(probleme_data)

combinations = get_product_product_combination()
combination_data = []
att_dupl = []
# # # # # # # article ayant deux valeur du meme attribut
archiv_product = []
probleme_variante_tmpl = []
for comb in combinations:
    if (comb[1], comb[2]) not in att_dupl:
        c = str(comb[2]).replace('{','').replace('}','')
        combination_data.append((c , comb[0]))
        att_dupl.append((comb[1], comb[2]))
    else:
        probleme_variante_tmpl.append(comb[1])
        archiv_product.append(comb[0])
update_probleme_variante_tmpl(probleme_variante_tmpl)
update_archive_product(archiv_product)


update_product_combination_indices(combination_data)
print('combination_indices done')



