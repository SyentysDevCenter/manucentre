# -*- coding: utf-8 -*-
import psycopg2


try:
    conn = psycopg2.connect("dbname='manucentre-master-640837' user='p_manucentre_master_640837' host='localhost' password='p_manucentre_master_640837' port='5432'")
except:
    print("I am unable to connect to the database")
cur = conn.cursor()

cur.execute("""select p.attribute_line_id,  pp.new_id, a.new_id, v.new_id from product_attribute_line p, product_table_map pp,
                product_attribute_map a, product_value_map v where pp.old_id = p.product_tmpl_id and 
                 a.old_id = p.attribute_id and v.old_id = p.value;""")
rows = cur.fetchall()
conn.close()
print('rooooows', len(rows), rows)
for row in rows:
    # with psycopg2.connect("dbname='manucentre-master-640837' user='p_manucentre_master_640837' host='localhost' password='p_manucentre_master_640837' port='5432'") as con:
    #     with con.cursor() as cur2:
    #         query = """select res_id from ir_model_data where name =%s and module = 'product_template';"""
    #         cur2.execute(query, ('3485',))
    #         prd_tmpl_id =  cur2.fetchall()
    #         if not prd_tmpl_id:
    #             print('nooooooot found pd_tmpl', row[1], prd_tmpl_id)
    #             continue
    # if not row[2]:
    #     attribute = False
    # with psycopg2.connect("dbname='manucentre-master-640837' user='p_manucentre_master_640837' host='localhost' password='p_manucentre_master_640837' port='5432'") as con:
    #     with con.cursor() as cur2:
    #         cur2.execute("""select res_id
    #                                     from ir_model_data
    #                                     where name = %s and module = 'product_attribute';""",(str(row[2]),))
    #         attribute = cur2.fetchall()
    #         if not attribute:
    #             print('nooooooot found attribute', row[2])
    #             # continue
    # with psycopg2.connect("dbname='manucentre-master-640837' user='p_manucentre_master_640837' host='localhost' password='p_manucentre_master_640837' port='5432'") as con:
    #     with con.cursor() as cur2:
    #         cur2.execute("""select res_id from ir_model_data where name = %s and module = 'product_attribute_value';""",(str(row[3]),))
    #         value = cur2.fetchall()
    #
    #         if not value:
    #             print('nooooooot found VALUE', row[3])
    #             # continue

    with psycopg2.connect(
                    "dbname='manucentre-master-640837' user='p_manucentre_master_640837' host='localhost' password='p_manucentre_master_640837' port='5432'") as con3:
        with con3.cursor() as cur3:
            old = cur3.execute("""SELECT res_id from ir_model_data where name = %s and module = 'product_template_attribute_line';""",
                               (str(row[0]),))
            old = cur3.fetchone()
            print('gggggggg',old)
            if old == None:

                with psycopg2.connect("dbname='manucentre-master-640837' user='p_manucentre_master_640837' host='localhost' password='p_manucentre_master_640837' port='5432'") as con2:
                    with con2.cursor() as cur2:
                        cur2.execute("""INSERT into product_template_attribute_line (active, product_tmpl_id, attribute_id) values (true,%s, %s)
                                            returning id;""",(row[1],row[2]))

                        con2.commit()
                        line = cur2.fetchone()[0]
                        print('lllllllll', line)
                if row[3] != None:
                    with psycopg2.connect(
                            "dbname='manucentre-master-640837' user='p_manucentre_master_640837' host='localhost' password='p_manucentre_master_640837' port='5432'") as con:
                        with con.cursor() as cur:
                            cur.execute("""INSERT into product_attribute_value_product_template_attribute_line_rel 
                            (product_attribute_value_id, product_template_attribute_line_id) values (%s, %s);""", (row[3], line))

                            con.commit()



                with psycopg2.connect(
                        "dbname='manucentre-master-640837' user='p_manucentre_master_640837' host='localhost' password='p_manucentre_master_640837' port='5432'") as con5:
                    with con5.cursor() as cur5:
                        xml_id =  cur5.execute("""INSERT into ir_model_data (name, module, model, res_id) values 
                                                (%s,'product_template_attribute_line', 'product.template.attribute.line', %s)
                                            ;""",(row[0], line))
                        con5.commit()
                with psycopg2.connect(
                                "dbname='manucentre-master-640837' user='p_manucentre_master_640837' host='localhost' password='p_manucentre_master_640837' port='5432'") as con4:
                    with con3.cursor() as cur4:
                        xml_id =  cur4.execute("""update product_attribute_line set new_line = %s where attribute_line_id = %s
                                            ;""",(line, row[0]))
                        con4.commit()
            else:

                if row[3] != None:

                    with psycopg2.connect(
                            "dbname='manucentre-master-640837' user='p_manucentre_master_640837' host='localhost' password='p_manucentre_master_640837' port='5432'") as con:
                        with con.cursor() as cur:
                            cur.execute("""select * from product_attribute_value_product_template_attribute_line_rel where 
                            product_attribute_value_id = %s and product_template_attribute_line_id = %s;""", (row[3], old[0]))

                            old_value = cur.fetchall()
                        if not old_value:
                            with psycopg2.connect(
                                    "dbname='manucentre-master-640837' user='p_manucentre_master_640837' host='localhost' password='p_manucentre_master_640837' port='5432'") as con:
                                with con.cursor() as cur:
                                    cur.execute("""INSERT into product_attribute_value_product_template_attribute_line_rel 
                                    (product_attribute_value_id, product_template_attribute_line_id) values (%s, %s) ;""", (row[3], old[0]))

                                    con.commit()






