from flask import Flask,render_template,request,redirect, url_for,flash
from flask_mysqldb import MySQL
from flask import g
import datetime
a = Flask(__name__)
a.config['MYSQL_HOST']='localhost'
a.config['MYSQL_USER']='root'
a.config['MYSQL_PASSWORD']='Ravi@123'
a.config['MYSQL_DB'] = 'root'
sql = MySQL(a)
@a.route('/')
def f0():
    company_name, cash = fetch_company_info()
    return render_template("login.html", company_name=company_name, cash=cash,)
@a.route('/login', methods=['GET', 'POST'])
def f2():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'login':
            username = request.form.get('username')
            password = request.form.get('password')
            if verify_user(username, password):
                return redirect(url_for('m1'))
            else:
                flash("Invalid username or password", "error")
    
    company_name, cash = fetch_company_info()
    return render_template("login.html", company_name=company_name, cash=cash)

@a.route('/main')
def m1():
    company_name, cash = fetch_company_info()
    return render_template("main.html", company_name=company_name, cash=cash)

@a.route('/items')
def I():
    company_name, cash = fetch_company_info() 
    items = fetch_items()
    return render_template("items.html", company_name=company_name, cash=cash, items=items)

@a.route('/add_item', methods=['POST'])
def add_i():
    item_name = request.form.get('item_name')
    alert_message = None
    
    if item_name:
        item_id = generate_item_id()
        if item_exists(item_name):
            alert_message = "Item already exists."
        else:
            insert_item(item_id, item_name)
    
    company_name, cash = fetch_company_info()
    items = fetch_items()
    return render_template("items.html", company_name=company_name, cash=cash, items=items, alert_message=alert_message)
@a.route('/edit_item/<item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if request.method == 'POST':
        new_item_name = request.form.get('new_item_name')
        if new_item_name:
            update_item(item_id, new_item_name)
            return redirect(url_for('I'))
    else:
        item = fetch_item_by_id(item_id)
        if item:
            return render_template('edit_i.html', item=item)
        else:
            return "Item not found."
@a.route('/purchase')
def P():
    company_name, cash = fetch_company_info() 
    items = fetch_items()
    return render_template("purchase.html", company_name=company_name, cash=cash, items=items)

@a.route('/add_purchase', methods=['POST'])
def add_purchase():
    company_name, cash = fetch_company_info()
    item_id = request.form.get('item_id')
    qty = int(request.form.get('qty'))
    rate = int(request.form.get('rate'))
    
    if item_id and qty and rate:
        purchase_id = generate_purchase_id()
        amount = qty * rate
        current_time = datetime.datetime.now() 
        update_balance_and_insert_purchase(company_name, purchase_id, item_id, qty, rate, amount, current_time)
        u1(item_id,qty)
    return redirect(url_for('P'))
@a.route('/view_purchases')
def view_purchases():
    company_name, cash = fetch_company_info() 
    purchases = fetch_purchases(company_name)
    alert_message = request.args.get('alert_message')
    return render_template("purchase.html", company_name=company_name, cash=cash, purchases=purchases)
@a.route('/sales')
def S():
    company_name, cash = fetch_company_info()
    purchases = fetch_purchases(company_name) 
    return render_template("sales.html", company_name=company_name, cash=cash, purchases=purchases)
@a.route('/add_sale', methods=['POST'])
def add_sale():
    company_name, cash = fetch_company_info()
    i_id = request.form.get('i_id')  
    rate = int(request.form.get('rate'))
    qty = int(request.form.get('qty'))
    
    available_qty = fetch_available_quantity(i_id)
    alert_message = None
    
    if qty > available_qty:
        alert_message = "Quantity exceeds available quantity."
    else:
        u_pur(qty, i_id)
        if i_id and rate and qty:
            s_id = generate_sale_id()
            amount = rate * qty
            current_time = datetime.datetime.now()
            update_balance_and_insert_sale(company_name, s_id, i_id, rate, qty, amount, current_time)
            alert_message = None
    
    return redirect(url_for('S', alert_message=alert_message))

@a.route('/view_sales')
def view_sales():
    company_name, cash = fetch_company_info()
    sales = fetch_sales(company_name)
    return render_template("sales.html", company_name=company_name, cash=cash, sales=sales)
@a.route('/Amount')
def Am():
    company_name, cash = fetch_company_info()
    return render_template("amount.html", company_name=company_name, cash=cash,)
@a.route('/add_amount', methods=['POST'])
def add_amount():
    company_name, cash = fetch_company_info()
    amount = int(request.form.get('Am'))

    if amount:
        update_company_balance(company_name, cash + amount)  
    return redirect(url_for('Am'))
def fetch_available_quantity(item_id):
    cur = sql.connection.cursor()
    cur.execute("SELECT qty FROM pur WHERE i_id = %s", (item_id,))
    available_quantity = cur.fetchone()
    cur.close()
    return available_quantity[0] if available_quantity else 0
def verify_user(username, password):
    cur = sql.connection.cursor()
    cur.execute("SELECT username FROM user WHERE username = %s AND password = %s", (username, password))
    existing_user = cur.fetchone()
    cur.close()
    return existing_user is not None
def fetch_company_info():
    cur = sql.connection.cursor()
    cur.execute("SELECT c_name, cash FROM company")
    company_data = cur.fetchone()
    cur.close()
    if company_data:
        company_name, cash = company_data
        return company_name, cash
    else:
        return "Company Name Not Found", 0
def fetch_company_info1():
    cur = sql.connection.cursor()
    cur.execute("SELECT company_name, item_id FROM purchase")
    company_data = cur.fetchone()
    cur.close()
    if company_data:
        company_name, cash = company_data
        return company_name, cash
    else:
        return "Company Name Not Found", 0
def fetch_items():
    cur = sql.connection.cursor()
    cur.execute("SELECT item_id, item_name FROM item")
    items = cur.fetchall()
    cur.close()
    return items

def generate_item_id():
    cur = sql.connection.cursor()
    cur.execute("SELECT MAX(item_id) FROM item")
    last_id = cur.fetchone()[0]
    cur.close()
    
    if last_id:
        last_number = int(last_id[1:])  
        new_number = last_number + 1
        new_id = f"I{new_number:02}"  
    else:
        new_id = "I01"
    
    return new_id

def insert_item(item_id, item_name):
    cur = sql.connection.cursor()
    sql.connection.commit()
    name = item_name.lower()
    cur.execute("SELECT item_name FROM item WHERE item_name = %s", (name,))
    existing_purchase = cur.fetchone()
    
    if existing_purchase:
        print("item has aldredy exsists")
    else:
        cur.execute("INSERT INTO item (item_id, item_name) VALUES (%s, %s)", (item_id, name))
        sql.connection.commit()
    sql.connection.commit()
    cur.close()

def fetch_item_by_id(item_id):
    cur = sql.connection.cursor()
    cur.execute("SELECT item_id, item_name FROM item WHERE item_id = %s", (item_id,))
    item = cur.fetchone()
    cur.close()
    return item
def item_exists(item_name):
    cur = sql.connection.cursor()
    cur.execute("SELECT item_name FROM item WHERE item_name = %s", (item_name.lower(),))
    existing_item = cur.fetchone()
    cur.close()
    return existing_item is not None

def update_item(item_id, new_item_name):
    cur = sql.connection.cursor()
    cur.execute("UPDATE item SET item_name = %s WHERE item_id = %s", (new_item_name, item_id))
    sql.connection.commit()
    cur.close()
def generate_purchase_id():
    cur = sql.connection.cursor()
    cur.execute("SELECT MAX(p_id) FROM purchase")
    last_id = cur.fetchone()[0]
    cur.close()
    
    if last_id:
        last_number = int(last_id[1:])  
        new_number = last_number + 1
        new_id = f"P{new_number:02}"  
    else:
        new_id = "P01"
    
    return new_id
def update_balance_and_insert_purchase(company_name, purchase_id, item_id, qty, rate, amount, time):
    cur = sql.connection.cursor()
    cur.execute("SELECT item_name FROM item WHERE item_id = %s", (item_id,))
    name = cur.fetchone()
    cur.execute("UPDATE company SET cash = cash - %s WHERE c_name = %s", (amount, company_name))
    cur.execute("INSERT INTO purchase (company_name, p_id, item_id, qty, rate, amount, time,i_name) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)",
                (company_name, purchase_id, item_id, qty, rate, amount, time,name))
    sql.connection.commit()
    cur.close()
def u1( item_id, qty):
    cur = sql.connection.cursor()
    cur.execute("SELECT item_name FROM item WHERE item_id = %s", (item_id,))
    name = cur.fetchone()
    cur.execute("SELECT i_id FROM pur WHERE i_id = %s", (item_id,))
    existing_purchase = cur.fetchone()
    
    if existing_purchase:
        sql.connection.rollback() 
        cur.execute("UPDATE pur SET qty = qty + %s WHERE i_id = %s", (qty, item_id))
    else:
        cur.execute("INSERT INTO pur (name, qty,i_id) VALUES ( %s, %s,%s)",
                (name, qty,item_id))
        sql.connection.commit()
    sql.connection.commit()
    cur.close()
def u_pur(qty,i_id):
    cur = sql.connection.cursor()
    cur.execute("UPDATE pur SET qty = qty - %s WHERE i_id = %s", (qty,i_id))
    sql.connection.commit()
    cur.close()
def update_company_balance(company_name, new_balance):
    cur = sql.connection.cursor()
    cur.execute("UPDATE company SET cash = %s WHERE c_name = %s", (new_balance, company_name))
    sql.connection.commit()
    cur.close()
def fetch_purchases(company_name):
    cur = sql.connection.cursor()
    cur.execute("SELECT p_id, time, item_id, qty, rate, amount FROM purchase WHERE company_name = %s", (company_name,))
    purchases = cur.fetchall()
    
    purchases_with_item_name = []
    for purchase in purchases:
        item_id = purchase[2]
        item_name = fetch_item_name_by_id(item_id)  
        purchases_with_item_name.append(purchase + (item_name,))
    
    cur.close()
    return purchases_with_item_name
def update_balance_and_insert_sale(company_name, s_id, i_id, rate, qty, amount, time):
    cur = sql.connection.cursor()
    cur.execute("SELECT item_name FROM item WHERE item_id = %s", (i_id,))
    name = cur.fetchone()
    cur.execute("UPDATE company SET cash = cash + %s WHERE c_name = %s", (amount, company_name))
    cur.execute("INSERT INTO sales (company_name, s_id, i_id, rate, qty, amount, time,i_name) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)",
                (company_name, s_id, i_id, rate, qty, amount, time,name))
    sql.connection.commit()
    cur.close()

def fetch_sales(company_name):
    cur = sql.connection.cursor()
    cur.execute("SELECT s_id, i_id, rate, qty, amount,time,i_name FROM sales WHERE company_name = %s", (company_name,))
    sales = cur.fetchall()
    cur.close()
    return sales
def generate_sale_id():
    cur = sql.connection.cursor()
    cur.execute("SELECT MAX(s_id) FROM sales")
    last_id = cur.fetchone()[0]
    cur.close()
    
    if last_id:
        last_number = int(last_id[1:])  
        new_number = last_number + 1
        new_id = f"S{new_number:02}"  
    else:
        new_id = "S01"
    
    return new_id
def fetch_item_name_by_id(item_id):
    cur = sql.connection.cursor()
    cur.execute("SELECT item_name FROM item WHERE item_id = %s", (item_id,))
    item_name = cur.fetchone()
    cur.close()
    return item_name[0] if item_name else "Item Not Found"
if __name__ == '__main__':
    a.run(debug=True)