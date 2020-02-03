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
Loc_map = cfg.loc_map


def get_stock():
    try:
        connection = psycopg2.connect(user=SOURCE_USER,
                                      password=SOURCE_PASSWORD,
                                      host=SOURCE_HOST,
                                      port=SOURCE_PORT,
                                      database=SOURCE_DB)

        cursor = connection.cursor()
        query = """
                select sum(q.qty) as stock,q.product_id,q.company_id from stock_quant q, product_product pp, product_template pt, stock_location loc
                where q.product_id = pp.id and pt.id = pp.product_tmpl_id
                and pt.tracking = 'none' and q.lot_id is NULL and pp.active = True and loc.id = q.location_id 
                and loc.usage = 'internal'
                group by q.product_id,q.company_id
                having sum(q.qty)>0;
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

def create_stock_quant(lots):
    try:
        connection = psycopg2.connect(user = DEST_USER,
                                      password = DEST_PASSWORD,
                                      host = DEST_HOST,
                                      port = DEST_PORT,
                                      database = DEST_DB)

        cursor = connection.cursor()
        for lot in lots:
            print(lot)
            cursor.execute("INSERT INTO stock_quant "\
             "(product_id,company_id,location_id,quantity,reserved_quantity)"\
             " VALUES(%s,%s,%s,%s,%s)",
                           (lot[0],lot[1],lot[2],lot[3],lot[4]))
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

product_prod = odoov13.env['product.product']
product_prod_ids = product_prod.search(['|', ('active', '=', True), ('active', '=', False)])
product_prod_data = product_prod.read(product_prod_ids, ['old_id'])
dict_product_prod = {part['old_id']: part['id'] for part in product_prod_data}

stocks = get_stock()
stock_qty = []
for st in stocks:
    stock_qty.append(
        [dict_product_prod.get(st[1],False),Companies_map[str(st[2])],Loc_map[str(st[2])],st[0],0]
    )
create_stock_quant(stock_qty)

print('Stock done')
