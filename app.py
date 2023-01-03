import pymysql
from flask import *
app=Flask(__name__)

from functions import *
from cryptography.fernet import Fernet

con = pymysql.connect(host='localhost', user='root', password='', database='MyShop_DB')
app.secret_key='cjbcjhgiwudygfuw4686ojnnc<mwkhiutn'
@app.route("/signup", methods=["POST","GET"])
def main():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        phone = request.form['phone']


        # validation
        if ' ' not in name:
            return render_template('signup.html', message = "Names must be two words")
        elif '@' not in email:
            return render_template('signup.html', message="Invalid Email")
        elif len(password) < 8:
            return render_template('signup.html', message="Password must be 8 characters")
        elif password != confirm:
            return render_template('signup.html', message="Passwords do not match")
        elif len(phone) != 13:
            return render_template('signup.html', message="Invalid phone number. must be 13 characters")
        elif not phone.startswith("+"):
            return render_template('signup.html', message="Must start with a +")
        else:
            password=password_hash(password)


            connection = pymysql.connect(host='localhost', user='root', password='', database='MyShop_DB')
            sql = "INSERT INTO `signup`(`name`, `email`, `password`, `confirm`, `phone`) VALUES (%s,%s,%s,%s,%s)"
            cursor = connection.cursor()
            cursor.execute(sql, (name, email, password, confirm, phone))
            connection.commit()
            # return render_template("signup.html",message="Saved Successfully")
            return redirect('/signin')
    else:
        return render_template("signup.html")
from cryptography.fernet import Fernet

@app.route("/signin", methods=['POST','GET'])
def signin():
    if request.method== 'POST':

        email=request.form['email']
        password=request.form['password']

        con=pymysql.connect(host='localhost',user='root',password='',database='MyShop_DB')
        sql='select * from signup where email =%s'
        cursor=con.cursor()
        cursor.execute(sql, email)
        if cursor.rowcount==0:

            return render_template('signin.html', message='The email Address is not registered')
        elif cursor.rowcount == 1:
            session['key']= email
            row=cursor.fetchone()
            hashed_password = row[2]  # this is hashed password from database
            print('Hashed pass', hashed_password)
            # verify that the hshed password is the same as hashed pass from the database
            status = password_verify(password, hashed_password)
            print("Login Status", status)

            if status:
                sql = 'select * from signup where email = %s'
                cursor = con.cursor()
                cursor.execute(sql, email)
                row = cursor.fetchone()
                con.commit()
                cursor.close()


                session['name']=row[0]
                session['email']=row[1]
                return redirect('/getproducts')
            else:
                return redirect('/signin')

        else:
            return render_template('signin.html',message='error occurred')
    else:
        return render_template('signin.html')

@app.route('/')
def account():
    return render_template('account.html')
@app.route("/logout")
def logout():
    #session.pop('user_id', None)
    session.clear()
    return redirect('/signin')


@app.route('/getproducts', methods=['POST','GET'])
def getproducts():
    if request.method == 'POST':
        name=request.form['name']

        con = pymysql.connect(host='localhost', user='root', password='', database='MyShop_DB')
        sql = "SELECT * FROM `products` where product_name LIKE '%{}%' ".format(name)
        cursor = con.cursor()
        # EXECUTE SQL
        cursor.execute(sql)
        if cursor.rowcount == 0:
            #
            return render_template('products.html', message="No products")
        else:
            rows = cursor.fetchall()
            return render_template('products.html', rows=rows)
    else:
        con = pymysql.connect(host='localhost', user='root', password='', database='MyShop_DB')
        sql = "SELECT * FROM `products`"
        cursor = con.cursor()
        # EXECUTE SQL
        cursor.execute(sql)
        if cursor.rowcount == 0:
            #
            return render_template('products.html', message="No products")
        else:
            rows = cursor.fetchall()
            return render_template('products.html', rows=rows)




    # assingment do the same to get appointments

# single item
@app.route('/single/<product_id>')
def single(product_id):
    connection = pymysql.connect(host='localhost', user='root', password='', database='MyShop_DB')
    sql = "SELECT * FROM `products` WHERE product_id = %s"
    cursor = connection.cursor()
    # EXECUTE SQL
    cursor.execute(sql,(product_id))
    row = cursor.fetchone()
    return render_template('single.html', row = row)



# impesa integration
import requests

  # flask object takes the the name of the application
import datetime
import base64
from requests.auth import HTTPBasicAuth
@app.route('/mpesa_payment', methods = ['POST','GET'])
def mpesa_payment():
        if request.method == 'POST':
            phone = str(request.form['phone'])
            amount = str(request.form['amount'])
            # GENERATING THE ACCESS TOKEN
            #J4VsULza2T57hrnZLqSAT5Am9wLI4G20
            # consumer_key = "J4VsULza2T57hrnZLqSAT5Am9wLI4G20"
            # consumer_secret = "caTx8W0AI1wk3Up2"
            consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
            consumer_secret = "amFbAoUByPV2rM5A"

            api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" #AUTH URL



            r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

            data = r.json()
            access_token = "Bearer" + ' ' + data['access_token']

            #  GETTING THE PASSWORD
            timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
            business_short_code = "174379"
            data = business_short_code + passkey + timestamp
            encoded = base64.b64encode(data.encode())
            password = encoded.decode('utf-8')


            # BODY OR PAYLOAD
            payload = {
                "BusinessShortCode": "174379",
                "Password": "{}".format(password),
                "Timestamp": "{}".format(timestamp),
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,  # use 1 when testing
                "PartyA": phone,  # change to your number
                "PartyB": "174379",
                "PhoneNumber": phone,
                "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
                "AccountReference": "account",
                "TransactionDesc": "account"
            }

            # POPULAING THE HTTP HEADER
            headers = {
                "Authorization": access_token,
                "Content-Type": "application/json"
            }

            url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" #C2B URL

            response = requests.post(url, json=payload, headers=headers)
            print (response.text)
            return render_template('payment.html', msg = 'Please Complete Payment in Your Phone')
        else:
            return redirect('/single/{{row[1]}}')


# add to cart route
@app.route('/add', methods=['POST'])
def add_product_to_cart():
        _quantity = int(request.form['quantity'])
        _code = request.form['code']
        # validate the received values
        if _quantity and _code and request.method == 'POST':
            cursor = con.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM products WHERE product_id= %s", _code)
            row = cursor.fetchone()
            #An array is a collection of items stored at contiguous memory locations. The idea is to store multiple items of the same type together

            itemArray = {str(row['product_id']): {'product_name': row['product_name'], 'product_id': row['product_id'], 'quantity': _quantity, 'product_cost': row['product_cost'],
                              'image_url': row['image_url'], 'total_price': _quantity * row['product_cost'],
                                             'product_brand': row['product_brand']}}
            print((itemArray))


            all_total_price = 0
            all_total_quantity = 0
            session.modified = True
            #if there is an item already
            if 'cart_item' in session:
                #check if the product you are adding is already there
                print("The test cart",type(row['product_id']) )
                print("session hf", session['cart_item'])
                if str(row['product_id']) in session['cart_item']:
                    print("reached here 1")


                    for key, value in session['cart_item'].items():
                        #check if product is there
                        if str(row['product_id']) == key:
                            print("reached here 2")
                            #take the old quantity  which is in session with cart item and key quantity
                            old_quantity = session['cart_item'][key]['quantity']
                            #add it with new quantity to get the total quantity and make it a session
                            total_quantity = old_quantity + _quantity
                            session['cart_item'][key]['quantity'] = total_quantity
                            #now find the new price with the new total quantity and add it to the session
                            session['cart_item'][key]['total_price'] = total_quantity * row['product_cost']

                else:
                    print("reached here 3")
                    #a new product added in the cart.Merge the previous to have a new cart item with two products
                    session['cart_item'] = array_merge(session['cart_item'], itemArray)


                for key, value in session['cart_item'].items():
                    individual_quantity = int(session['cart_item'][key]['quantity'])
                    individual_price = float(session['cart_item'][key]['total_price'])
                    all_total_quantity = all_total_quantity + individual_quantity
                    all_total_price = all_total_price + individual_price

            else:
                #if the cart is empty you add the whole item array
                session['cart_item'] = itemArray
                all_total_quantity = all_total_quantity + _quantity
                #get total price by multiplyin the cost and the quantity
                all_total_price = all_total_price + _quantity * float(row['product_cost'])


            #add total quantity and total price to a session
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price
            return redirect(url_for('.cart'))
        else:
            return 'Error while adding item to cart'

# function for joining arrays , we have the first array and second array
# if a customer adds an item to a cart ,we take note,
# if they aadd another item , then merge the arrays to get the total items in one list

def array_merge( first_array, second_array ):
     if isinstance( first_array , list) and isinstance( second_array , list ):
      return first_array + second_array
     #takes the new product add to the existing and merge to have one array with two products
     elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
      return dict( list( first_array.items() ) + list( second_array.items() ) )
     elif isinstance( first_array , set ) and isinstance( second_array , set ):
      return first_array.union( second_array )
     return False

# delete route
@app.route('/delete/<string:code>')
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True
        for item in session['cart_item'].items():
            if item[0] == code:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break

        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

        # return redirect('/') the cart function
        return redirect(url_for('.cart'))
    except Exception as e:
        print(e)
# empty cart route
@app.route('/empty')
def empty_cart():
    try:
        if 'cart_item' in session or 'all_total_quantity' in session or 'all_total_price' in session:
            session.pop('cart_item', None)
            session.pop('all_total_quantity', None)
            session.pop('all_total_price', None)
            return redirect(url_for('.cart'))
        else:
            return redirect(url_for('.cart'))

    except Exception as e:
        print(e)

#
@app.route('/cart')
def cart():
    return render_template('cart.html')

def check_customer():
    if 'email' in session:
        return True
    else:
        return False


@app.route('/customer_checkout')
def customer_checkout():
    if check_customer():
            return redirect('/cart')
    else:
        return redirect('/signin')



# # checkout route
# from  order_gen import random_string_generator
# #checkout route
# @app.route('/proceed_checkout', methods = ['POST','GET'])
# def proceed_checkout():
#     if check_customer():
#         if 'cart_item' in  session:
#             if request.method == 'POST':
#                 mpesa_code = request.form['mpesa_code']
#                 all_total_price = 0
#                 all_total_quantity = 0
#                 # Need to check database******************
#                 order_code = random_string_generator()
#                 for key, value in session['cart_item'].items():
#                     individual_quantity = int(session['cart_item'][key]['quantity'])
#                     individual_price = float(session['cart_item'][key]['total_price'])
#                     product_id = session['cart_item'][key]['product_id']
#                     product_name = session['cart_item'][key]['product_name']
#                     product_cost = session['cart_item'][key]['product_cost']
#
#                     all_total_quantity = all_total_quantity + individual_quantity
#                     all_total_price = all_total_price + individual_price
#                     print('Individual qqty',individual_quantity)
#                     print('Individual price',individual_price)
#                     print('product_id', product_id)
#                     print('product name', product_name)
#                     print('Total qtty', all_total_quantity)
#                     print('Total price', all_total_price)
#                     print("=================")
#                     email = session['tel']
#                     #session
#                     if not email:
#                         flash('Sorry, Error Occured during checkout, Try Again', 'danger')
#                         return redirect('/signin')
#                     elif not individual_price or not individual_quantity or not product_id or not product_name or not all_total_price or not all_total_quantity:
#                         flash('Sorry, Error Occured during checkout, Try Again', 'danger')
#                         return redirect('/cart')
#                     else:
#                         try:
#                             sql = 'INSERT INTO `orders`(`product_name`, `product_qtty`, `product_cost`, `email`, `order_code`, `mpesa_confirmation`, `individual_total`, `all_total_price`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
#                             cursor = con.cursor()
#                             cursor.execute(sql, (product_name, individual_quantity, product_cost, email, order_code, mpesa_code, individual_price, all_total_price))
#                             con.commit()
#
#                         except Exception as e:
#                             print(e)
#                             flash('Sorry, Error occured during checkout, Please try again','danger')
#                             return redirect('/cart')
#
#                 print('================')
#                 print('Total qtty', all_total_quantity)
#                 print('Total price', all_total_price)
#                 try:
#                     sql2 = 'update orders set all_total_price = %s where order_code = %s'
#                     cursor = con.cursor()
#                     #it updates all the products to have the same price in the same order in the all total price column
#                     cursor.execute(sql2,(all_total_price, order_code))
#                     con.commit()
#                     flash('Your Order is Complete, Please check your Orders in Your Profile','success')
#                     session.pop('cart_item', None)
#                     session.pop('all_total_quantity', None)
#                     session.pop('all_total_price', None)
#                     print('here')
#                     return redirect(url_for('cart'))
#                 except:
#                     flash('Sorry, Error occured during checkout, Please try again','danger')
#                     session.pop('cart_item', None)
#                     session.pop('all_total_quantity', None)
#                     session.pop('all_total_price', None)
#                     return redirect('/cart')
#             else:
#                 return redirect('/cart')
#         else:
#             return redirect('/cart')
#     else:
#         flash('You must be logged in to Make a Purchase, Please Login', 'warning')
#         return redirect('/signin')

app.run(debug=True)







