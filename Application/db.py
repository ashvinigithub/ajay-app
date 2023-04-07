import sqlite3

import click
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, send_file, g, jsonify, make_response
import os
import os.path

app = Flask(__name__)
app.config['DEBUG'] = True

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = dbpath = os.path.join(basedir, r'database/sqlite-ajay-db.db')



def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    CURSOR = get_db().cursor()
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def query_dict_db(query, args=(), one=False):
    conn = sqlite3.connect(dbpath)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    dataset = cursor.execute(query)
    result = dataset.fetchall()
    list_of_dictionaries = []
    for i in result:
        list_of_dictionaries.append(dict(i))
    cursor.close()
    return list_of_dictionaries


@app.route('/', methods=['GET'])
def home():
    global CURSOR, dbpath, DATABASE, CUSTOMER_NAMES, ITEM_NAMES
    rv1 = query_db('''
    Select distinct UPPER(A.Customer_ID || ' | ' || A.Customer_Name || ' | ' ||  A.Contact_No || ' | ' ||  A.Address || ' | ' || COALESCE(B.SALE_DATE, '')  || ' | ' || COALESCE(B.OLD_PENDING_AMOUNT_DATE, '') || ' | ' || COALESCE(B.OLD_PENDING_AMOUNT, 0) ) AS cust_info 
    from ajay_app_customer_master A
    left join (Select * from (
    select CUSTOMER_ID, SALE_DATE, OLD_PENDING_AMOUNT_DATE, OLD_PENDING_AMOUNT, 
    ROW_NUMBER() OVER(partition BY CUSTOMER_ID order by OLD_PENDING_AMOUNT_DATE DESC, SALE_DATE DESC) AS Rnk 
    from ajay_app_Retail_Sale 
    where COALESCE(TRIM(OLD_PENDING_AMOUNT_DATE), '') <> '' 
    ) R where Rnk = 1) AS B 
    ON A.customer_id = B.CUSTOMER_ID  ORDER BY A.Customer_ID DESC;
    ''')
    CUSTOMER_NAMES = clear_sql_output(rv1)

    rv2 = query_db('''
    Select DISTINCT TRIM(ITEM_NAME) AS  ITEM_NAME from ajay_app_Retail_Sale where COALESCE(TRIM(ITEM_NAME), '') NOT IN ('', '0') ORDER BY 1 ;
    ''')
    ITEM_NAMES = clear_sql_output(rv2)

    return render_template('retailsale.html', Customer_Names= CUSTOMER_NAMES, item_names = ITEM_NAMES)




@app.route("/save_retailsale_to_db", methods=["POST","GET"])
def save_retailsale_to_db():
    _customer_id = request.form.get("_customer_id")
    _metalname = request.form.get("_metalname")
    _productinfo = request.form.get("_productinfo")
    _purity = request.form.get("_purity")
    _hsncode = request.form.get("_hsncode")
    _gross_weight = request.form.get("_gross_weight")
    _quantity = request.form.get("_quantity")
    _less_weight = request.form.get("_less_weight")
    _net_weight = request.form.get("_net_weight")
    _rate = request.form.get("_rate")
    _makelabourpergms = request.form.get("_makelabourpergms")
    _makechargesfinal = request.form.get("_makechargesfinal")
    _finaltotal = request.form.get("_finaltotal")
    _total_amount = request.form.get("_total_amount")
    _discount_percentage = request.form.get("_discount_percentage")
    _net_amount = request.form.get("_net_amount")
    _gst_amount = request.form.get("_gst_amount")
    _gross_amount = request.form.get("_gross_amount")
    _discount_amount_inr = request.form.get("_discount_amount_inr")
    _amount_received = request.form.get("_amount_received")
    _balance_amount = request.form.get("_balance_amount")
    _set_alarm_date = request.form.get("_set_alarm_date")
    _paymethod = request.form.get("_paymethod")

    print(_customer_id, _metalname, _productinfo, _purity, _paymethod, _gst_amount, _balance_amount)
    return jsonify(success=True)


##################################################################################################################
###################################################### customer_details ##########################################
##################################################################################################################

def clear_sql_output(rv):
    l = []
    for i in rv:
        i = str(i).strip()[2:-3]
        l.append(i)
    return l


@app.route('/customer_details', methods=['GET'])
def customer_details():
    rv = query_db('SELECT distinct upper(Customer_Name) AS  Customer_Name FROM ajay_app_customer_master;')
    Customer_Names = clear_sql_output(rv)
    return render_template('customer_details.html' , verdict='Success', Customer_Names= Customer_Names)


@app.route("/getcustomernameslist",methods=["POST","GET"])
def getcustomernameslist():
    # selected_schema = request.form.get("selected_schema")
    rv = query_db('SELECT distinct upper(Customer_Name) AS  Customer_Name FROM ajay_app_customer_master order by 1;')
    list_of_tables = str([i[0] for i in rv])[1:-1]
    return list_of_tables


@app.route("/getcustomerinfo",methods=["POST","GET"])
def getcustomerinfo():
    customernameasparameter = request.form.get("customernameasparameter")
    print(customernameasparameter)
    returned_list_of_dictionaries = query_dict_db(f'''
        SELECT distinct trim(upper(Customer_Name)) AS "Customer Name", Customer_ID AS "X DB Key", COALESCE(Contact_no, '0') AS "Mobile Number", upper(COALESCE(Address, '0')) AS  Address 
        FROM ajay_app_customer_master where trim(upper(Customer_Name)) = '{customernameasparameter}';
    ''')
    return returned_list_of_dictionaries


@app.route("/getcustomerdata", methods=["POST","GET"])
def getcustomerdata():
    customernameasparameter = request.form.get("customernameasparameter")
    print(customernameasparameter)
    returned_list_of_dictionaries = query_dict_db(f'''
        Select DISTINCT CUSTOMER_ID AS "0_X DB Key", COALESCE(SALE_DATE, '0001-01-01') AS "1_SALES DATE", 
        COALESCE(upper(GROUP_NAME), 'N/A') AS "2_TYPE OF ITEM", 
        COALESCE(upper(ITEM_NAME), 'N/A') AS "3_ITEM NAME", 
        COALESCE(WEIGHT, '0.00') AS "4_WEIGHT", 
        COALESCE(RATE_GM, '0.00') AS "5_RATE", 
        COALESCE(LABOUR_RATE, '0.00') AS "6_LABOUR RATE", 
        COALESCE(TOTAL_AMOUNT, '0.00') AS "7_TOTAL AMOUNT", 
        COALESCE(PAID_AMOUNT, '0.00') AS "8_PAID AMOUNT", 
        COALESCE(BALANCE_AMOUNT, '0.00') AS "9_BALANCE AMOUNT"
        from Retail_Sale 
        where CUSTOMER_ID in (Select CUSTOMER_ID FROM ajay_app_customer_master where Contact_no IN 
        (Select distinct Contact_no  from Customer_Master where trim(upper(Customer_Name)) = '{customernameasparameter}') 
        ) AND CUSTOMER_ID IN (Select CUSTOMER_ID FROM ajay_app_customer_master where trim(upper(Customer_Name)) = '{customernameasparameter}')
                ORDER BY SALE_DATE DESC;
        ''')
    return returned_list_of_dictionaries


@app.route("/gettableslist",methods=["POST","GET"])
def gettableslist():
    # selected_schema = request.form.get("selected_schema")
    rv = query_db('SELECT distinct upper(Customer_Name) AS  Customer_Name FROM ajay_app_customer_master order by 1;')
    list_of_tables = str([i[0] for i in rv])[1:-1]
    return list_of_tables

##################################################################################################################
###################################################### Retail Sale ###############################################
##################################################################################################################


@app.route("/getratesforretailsalepage", methods=["POST","GET"])
def getratesforretailsalepage():
    purityparameter = request.form.get("purityparameter")
    q = (f'''
    Select * from ajay_app_gold_rate_master where RATE_DATE IN 
    (Select max(RATE_DATE) from ajay_app_gold_rate_master where PURITY = '{purityparameter}') 
    and PURITY = '{purityparameter}' ;
    ''')
    returned_list_of_dictionaries = query_dict_db(q)
    print(purityparameter, returned_list_of_dictionaries)
    print(q)
    return returned_list_of_dictionaries


##################################################################################################################
###################################################### RATES #####################################################
##################################################################################################################


@app.route('/rates', methods=['GET'])
def rates():
    rv = query_db('SELECT * FROM ajay_app_gold_rate_master;')
    rates = clear_sql_output(rv)
    return render_template('rates.html' , verdict='Success', rates= rates)


@app.route("/ratespagedata", methods=["POST","GET"])
def ratespagedata():
    returned_list_of_dictionaries = query_dict_db(f'''
    Select * from ajay_app_gold_rate_master order by RATE_DATE DESC;
        ''')
    return returned_list_of_dictionaries


@app.route("/updateratesfortoday", methods=["POST","GET"])
def updateratesfortoday():
    rate_24k = request.form.get("rate_24k") 
    rate_24k = float((rate_24k if rate_24k else 0.00)) / 10.0000
    rate_22k = float(22/24.00) * rate_24k
    rate_20k = float(20/24.00) * rate_24k
    rate_18k = float(18/24.00) * rate_24k
    rate_16k = float(16/24.00) * rate_24k
    rate_14k = float(14/24.00) * rate_24k
    rate_12k = float(12/24.00) * rate_24k
    rate_10k = float(10/24.00) * rate_24k
    rate_9k = float(9/24.00) * rate_24k
    rate_silver = request.form.get("rate_silver")
    rate_silver = float((rate_silver if rate_silver else 0.00)) / 10.0000

    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    rate_dict = {"24k": rate_24k, "22k": rate_22k, "20k": rate_20k, "18k": rate_18k, "16k": rate_16k, 
    "14k": rate_14k, "12k": rate_12k, "10k":rate_10k, "9k": rate_9k, "Silver-P": rate_silver, "Silver": (rate_silver * 0.90)}

    for key, value in rate_dict.items(): 
        if (value != 0.00 and (key != 'Silver' or key != 'Silver-P')):
            try:
                cursor.execute(f'''
                INSERT INTO ajay_app_gold_rate_master (METAL_TYPE, PURITY, RATE, RATE_DATE, INSERT_DATE) 
                VALUES('GOLD', '{key}', {value}, current_date, CURRENT_TIMESTAMP);
                    ''')
                conn.commit()
            except:
                pass
            
        elif (value != 0.00 and (key == 'Silver' or key == 'Silver-P')):
            try:
                cursor.execute(f'''
                INSERT INTO ajay_app_gold_rate_master (METAL_TYPE, PURITY, RATE, RATE_DATE, INSERT_DATE) 
                VALUES('SILVER', '{key}', {value}, current_date, CURRENT_TIMESTAMP);
                    ''')
                conn.commit()
            except:
                pass
    del rate_dict
    conn.close()
    return jsonify(success=True)


@app.route("/deleteratesentry", methods=["POST","GET"])
def deleteratesentry():
    selecteddeletedate = request.form.get("selecteddeletedate")
    selecteddeletedate = str(selecteddeletedate).strip()
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(f'''
        DELETE FROM ajay_app_gold_rate_master where RATE_DATE = '{selecteddeletedate}' ;
        ''')
    conn.commit()
    return jsonify(success=True)



##################################################################################################################
###################################################### Add/Update Customer ####################################### 
##################################################################################################################


@app.route('/add_customer', methods=['GET'])
def add_customer():
    return render_template('add_customer.html' , Customer_Names= CUSTOMER_NAMES)


################################# Update Customer #################################################################
@app.route("/updatecustomerinfo", methods=["POST","GET"])
def updatecustomerinfo():
    cust_id = request.form.get("customer_id")
    updated_cust_name = request.form.get("updated_cust_name")
    updated_mobile_number = request.form.get("updated_mobile_number")
    updated_address = request.form.get("updated_address")
    updated_pan = request.form.get("updated_pan")
    updated_adhaar = request.form.get("updated_adhaar")
    updated_dob = request.form.get("updated_dob")
    # print(cust_id)
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    query = f'''
    UPDATE
        ajay_app_customer_master
    SET
        customer_name = '{updated_cust_name}',
        Address = '{updated_address}',
        contact_no = '{updated_mobile_number}',
        customer_pan_card = '{updated_pan}',
        customer_adhaar_card = '{updated_adhaar}'
    WHERE
        customer_id = {cust_id};
        '''
    cursor.execute(query)
    conn.commit()
    return jsonify(success=True)


################################# Insert a NEW Customer #################################################################
@app.route("/insert_new_customer", methods=["POST","GET"])
def insert_new_customer():
    new_cust_name = request.form.get("new_cust_name")
    new_mobile_number = request.form.get("new_mobile_number")
    new_address = request.form.get("new_address")
    new_pan = request.form.get("new_pan")
    new_adhaar = request.form.get("new_adhaar")
    new_dob = request.form.get("new_dob")
    print(new_cust_name, new_mobile_number)
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    query = f'''
            INSERT INTO ajay_app_customer_master 
            (customer_id, customer_name, Address, contact_no, Opening_Amount, Opening_Date, customer_pan_card, customer_adhaar_card, Alarm_Date, Alarm_Id, Alarm_Status, Nerration, Category_Type, TRIAL483) 
            VALUES((Select max(customer_id) + 1 from ajay_app_customer_master), '{new_cust_name}', '{new_address}', '{new_mobile_number}', 0, current_date, '{new_pan}', '{new_adhaar}', '', 0, '', '', '', '');
        '''
    cursor.execute(query)
    conn.commit()
    return jsonify(success=True)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)