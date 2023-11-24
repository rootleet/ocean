import pyodbc

from ocean.settings import RET_DB_HOST, RET_DB_PORT, RET_DB_NAME, RET_DB_USER, RET_DB_PASS


def ret_cursor(host=RET_DB_HOST, port=RET_DB_PORT, db=RET_DB_NAME, user=RET_DB_USER, password=RET_DB_PASS):
    server = f"{host}"
    database = db
    username = user
    password = password
    driver = '{ODBC Driver 17 for SQL Server}'  # Change this to the driver you're using
    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    connection = pyodbc.connect(connection_string)
    return connection.cursor()


def get_stock(item_code):
    stock_cursor = ret_cursor()
    query = f"SELECT stock.loc_id, (select br_name from branch where br_code = stock.loc_id ) as loc_name , isnull(sum(qty),0) as qty, ('2') as trtype, stock_price.avg_cost, stock_price.last_net_cost, stock_price.last_rec_supp, stock_price.last_rec_price, stock_price.local_supp_curr, stock_price.last_rec_date, stock_price.last_cost2, stock_price.last_cost3, isnull(sum(stock.item_wt),0) as tot_wt, stock_price.last_rec_um FROM stock LEFT OUTER JOIN stock_price ON stock.item_code = stock_price.item_code AND stock.loc_id = stock_price.loc_id, user_loc_access ,prod_mast WHERE ( user_loc_access.loc_id = stock.loc_id ) and ( stock.item_code = prod_mast.item_code ) and( ( stock.item_code = '{item_code}' ) AND ( user_loc_access.loc_access = '1' ) AND ( user_loc_access.user_id = '411' ) AND( prod_mast.item_type in ('1','3','5','7')) ) GROUP BY stock.loc_id, stock_price.avg_cost, stock_price.last_net_cost, stock_price.last_rec_price, stock_price.last_rec_um, stock_price.local_supp_curr, stock_price.last_rec_supp, stock_price.last_rec_date, stock_price.last_cost2, stock_price.last_cost3 UNION SELECT stock_chk.loc_id, (select br_name from branch where br_code = stock_chk.loc_id ) as loc_name , isnull(sum(qty),0) as qty, '3', stock_price.avg_cost, stock_price.last_net_cost, stock_price.last_rec_supp, stock_price.last_rec_price, \
    stock_price.local_supp_curr, stock_price.last_rec_date, stock_price.last_cost2,stock_price.last_cost3, isnull(sum(stock_chk.item_wt),0) as tot_wt, stock_price.last_rec_um FROM stock_chk LEFT OUTER JOIN stock_price ON stock_chk.item_code = stock_price.item_code AND stock_chk.loc_id = stock_price.loc_id ,user_loc_access ,prod_mast \
    WHERE  ( user_loc_access.loc_id = stock_chk.loc_id ) and ( stock_chk.item_code = prod_mast.item_code ) and ( ( stock_chk.item_code = '{item_code}' ) AND ( user_loc_access.loc_access = '1' ) AND ( user_loc_access.user_id = '411' ) AND( prod_mast.item_type in ('1','3','5','7')))  GROUP BY stock_chk.loc_id, stock_price.avg_cost, stock_price.last_net_cost, stock_price.last_rec_supp, stock_price.last_rec_price, stock_price.last_rec_um, stock_price.local_supp_curr, stock_price.last_rec_date, stock_price.last_cost2, stock_price.last_cost3 ORDER BY 1 ASC "

    stock_cursor.execute(query)
    nia = 0
    osu = 0
    spintex = 0
    kicthen = 0
    warehouse = 0

    for row in stock_cursor.fetchall():

        loc_id = row[0]
        qty = row[2]

        if loc_id == '001':
            spintex += qty

        if loc_id == '202':
            nia += qty

        if loc_id == '205':
            osu += qty

        if loc_id == '201':
            kicthen += qty

        if loc_id == '999':
            warehouse += qty


    return {
        'nia': nia,
        'osu': osu,
        'spintex': spintex,
        'kitchen': kicthen,
        'warehouse': warehouse
    }

