import pyrebase
import common 
import firebase
from datetime import datetime
from collections import defaultdict
from flask import Flask, render_template, request, redirect, session

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
            
            auth.sign_in_with_email_and_password(e, p)
            session['email_name'] = e
            session.permanent = True
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
    if 'email_name' not in session:
        return redirect('/login')  
    
    total_quantity = 0
    total_amount = 0
    
    for item in common.productadd:
        total_quantity += item['qty']
        total_amount += item['price'] * item['qty']
    
    return render_template(
        "home.html", 
        products=common.products,
        quantity=total_quantity,
        total=total_amount
    )

@app.route('/addcard', methods=['GET', 'POST'])
def addcard():
    if 'email_name' not in session:
        return redirect('/login')
    if request.method == 'POST':
        id = int(request.form['product_id'])
        name = request.form['product_name']
        image = request.form['product_image']
        price = int(request.form['product_price'])
        qun = int(request.form['quantity'])

        for item in common.productadd:
            if item['id'] == id:
                item['qty'] = qun
                return redirect('/home') 
        
        
        common.productadd.append({
            "id": id,
            "name": name,
            "price": price,
            "image": image,
            "qty": qun
        })
        
        return redirect('/home') 
    

    total_quantity = 0
    total_amount = 0
    
    for item in common.productadd:
        total_quantity += item['qty']
        total_amount += item['price'] * item['qty']
    
    return render_template(
        "add.html", 
        product=common.productadd,
        quantity=total_quantity,
        total=total_amount
    )

@app.route('/remove/<int:pid>')
def remove_item(pid):
    for item in common.productadd:
        if item['id'] == pid:
            common.productadd.remove(item)
            return redirect('/addcard') 
    
    return redirect('/addcard')  

@app.route('/bill')
def bill():
    if 'email_name' not in session:
        return redirect('/login')
    current_time = datetime.now()
    total_price = sum(item['price'] * item['qty'] for item in common.productadd)

    tax = total_price * 0.1
    charge = total_price * 0.07
    final_total = total_price + tax + charge
    
    return render_template(
        "bill.html", 
        pro=common.productadd,
        totalprice=total_price,
        current_time=current_time,
        tax=tax,
        charge=charge,
        final_total=final_total
    )

@app.route('/increase/<pid>')
def increase_qty(pid):
    for item in common.productadd:
        if item['id'] == int(pid):
            item['qty'] += 1
            break
    
    return redirect('/addcard')  

@app.route('/decrease/<pid>')
def decrease_qty(pid):
    for item in common.productadd:
        if item['id'] == int(pid):
            item['qty'] -= 1
            if item['qty'] <= 0:
                common.productadd.remove(item)
            break
    
    return redirect('/addcard') 

@app.route('/account')
def account():
    if 'email_name' not in session:
        return redirect('/login')
    sn = session.get('email_name')
    return render_template("account.html",username="Krishna Patel",
        email=sn)
    
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store"
    return response

if __name__ == '__main__':
    app.run(debug=True)