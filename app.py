import pyrebase

import common 

import firebase
from datetime import datetime
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for,session,make_response

app = Flask(__name__)

app.secret_key = "KPTHEFOOD"

firebase = pyrebase.initialize_app(firebase.config)
auth = firebase.auth()

@app.route('/')
def main():
    return render_template("mainpage.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        e = request.form['email']
        p = request.form['password']
        
        try:
            session['user_name'] = e
            auth.sign_in_with_email_and_password(e, p)
            return redirect('/home')
        except:
            return redirect("/login")
            
    return render_template('login.html')

@app.route('/manu')
def manu():
    return render_template('manu.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/signup', methods=['GET','POST'])
def signup():
    msg = ""
    if request.method == 'POST':
        e = request.form['email']
        p = request.form['password']
        try:
            auth.create_user_with_email_and_password(e, p)
            return redirect('/login')
        except:
            msg = "Error creating account"
    return render_template('signup.html', msg=msg)

@app.route("/home")
def home():
    if 'user_name' not in session:
        return redirect('/login')
    return render_template("home.html", products = common.products)

@app.route('/addcard', methods=['GET', 'POST'])
def addcard():

    if request.method == 'POST':
        id = request.form['product_id']
        name = request.form['product_name']
        image = request.form['product_image']
        price = request.form['product_price']

        common.productadd.append({
            "id": id,
            "name": name,
            "price": price,
            "image": image
        })

    return render_template("add.html", product=common.productadd)

@app.route('/remove/<int:pid>')
def remove_item(pid):

    for item in common.productadd:
        if str(item.get('id')) == str(pid):
            common.productadd.remove(item)
            return redirect('/addcard')

    return redirect('/home')

@app.route('/bill')
def bill():
    current_time = datetime.now()
    total_price = sum(float(product['price']) for product in common.productadd)
    tax = total_price * 0.1
    charge = total_price * 0.07
    final_total = total_price + tax + charge
    
    return render_template(
        "bill.html", 
        pro=common.productadd,
        totalprice = total_price ,
        current_time = current_time,
        tax = tax,
        charge = charge,
        final_total = final_total
        )


if __name__ == '__main__':
    app.run(debug=True)