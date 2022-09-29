import sqlite3


create_packages_query = '''CREATE TABLE IF NOT EXISTS packages(
                        package_id INTEGER  PRIMARY KEY NOT NULL UNIQUE,
                        address TEXT,
                        type TEXT,
                        amount INTEGER  NOT NULL,
                        price INT,
                        time DATETIME,
                        telegram_id INTEGER)'''
create_orders_query = '''CREATE TABLE IF NOT EXISTS orders(
                        order_id   INTEGER  PRIMARY KEY NOT NULL UNIQUE,
                        package_id INTEGER,
                        address TEXT,
                        type TEXT,
                        amount INTEGER,
                        price INT,
                        time DATETIME,
                        partner_telegram_id INTEGER,
                        client_telegram_id INTEGER,
                        code INTEGER,
                        stage TEXT)'''
create_partners_query = '''CREATE TABLE IF NOT EXISTS partners(
                           partner_id INTEGER PRIMARY KEY NOT NULL,
                           telegram_id INTEGER,
                           telegram_username TEXT)'''
get_all_packages_query = '''SELECT * FROM packages'''
get_actual_packages_query = '''SELECT * FROM packages 
                               WHERE time > DATE('now') AND amount > 0'''
insert_package_query = '''INSERT INTO packages VALUES(?, ?, ?, ?, ?, ?, ?)'''
delete_package_by_id_query = '''DELETE FROM packages WHERE package_id = {package_id}'''
decrease_package_query = '''UPDATE packages 
                            SET amount = amount - {amount} 
                            WHERE package_id = {package_id}'''
get_amount_query = '''SELECT amount FROM packages WHERE package_id = {package_id}'''
get_package_owner_query = '''SELECT telegram_id FROM packages WHERE package_id = {package_id}'''
get_package_by_id_query = '''SELECT * FROM packages WHERE package_id = {package_id}'''
add_order_query = '''INSERT INTO orders VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
set_order_amount_query = 'UPDATE orders SET amount={amount} WHERE package_id={package_id}'
complete_order_query = "UPDATE orders SET stage = 'completed' WHERE stage = 'in process' AND CODE = {code}"
get_order_by_code_query = 'SELECT * FROM orders WHERE code = {code}'
cancel_order_packs_query = "UPDATE packages SET amount = amount + {canceled_amount} WHERE package_id = {package_id}"
cancel_order_ords_query = "UPDATE orders SET stage = 'canceled' WHERE code = {code}"
get_package_id_by_code_query = 'SELECT package_id FROM orders WHERE code = {code}'
get_canceled_amount_query = 'SELECT amount FROM orders WHERE code = {code}'
get_all_partners_query = 'SELECT telegram_username FROM partners'


async def connect_to_database(database_name="packages.db"):
    global cur, base
    base = sqlite3.connect(database_name)
    cur = base.cursor()
    if base:
        print("Database is connected")
    base.execute(create_packages_query)
    base.execute(create_orders_query)
    base.execute(create_partners_query)
    base.commit()


def get_package_by_id(package_id):
    cur.execute(get_package_by_id_query.format(package_id=package_id))
    return cur.fetchall()[0]


def get_all_packages(actual_packages=True):  # time > current time -> True
    if actual_packages:
        return cur.execute(get_actual_packages_query).fetchall()
    else:
        return cur.execute(get_all_packages_query).fetchall()


async def add_package(state):
    async with state.proxy() as data:
        cur.execute(insert_package_query, (None,
                                           data['address'],
                                           data['type'],
                                           data['amount'],
                                           data['price'],
                                           data['time'],
                                           data['telegram_id']))
        base.commit()


def delete_package(package_id):
    base.execute(delete_package_by_id_query.format(package_id=package_id))
    base.commit()


def decrease_package(package_id, amount):
    base.execute(decrease_package_query.format(package_id=package_id, amount=amount))
    base.commit()


def get_package_amount(package_id):
    cur.execute(get_amount_query.format(package_id=package_id))
    return cur.fetchall()[0][0]


def get_package_owner_id(package_id):
    cur.execute(get_package_owner_query.format(package_id=package_id))
    return cur.fetchall()[0][0]


def add_order(package_id, amount, client_telegram_id, code):
    order = get_package_by_id(package_id)
    order = (None, ) + order + (client_telegram_id, code, 'in process')
    # print(order)
    base.execute(set_order_amount_query.format(amount=amount, package_id=package_id))
    base.execute(add_order_query, order)
    base.commit()


def complete_order(code):
    base.execute(complete_order_query.format(code=code))
    base.commit()


def get_order_by_code(code):
    return cur.execute(get_order_by_code_query.format(code=code)).fetchall()[0]


def cancel_order(code):
    pack_id = cur.execute(get_package_id_by_code_query.format(code=code)).fetchall()[0][0]
    canceled_amount = cur.execute(get_canceled_amount_query.format(code=code)).fetchall()[0][0]
    base.execute(cancel_order_packs_query.format(package_id=pack_id, canceled_amount=canceled_amount))
    base.execute(cancel_order_ords_query.format(code=code))
    base.commit()


def create_order_code(package_id, user_id):
    return str(cur.execute('SELECT MAX(order_id) FROM orders').fetchall()[0][0] + 1) +\
           str(user_id)[:3] + str(package_id)  # code = order_id + (3 last digits from user_id) + package_id


def get_all_partners():
    return cur.execute(get_all_partners_query).fetchall()[0]
