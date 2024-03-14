import re
from flask import Flask, render_template, request, redirect, session, sessions 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, request, redirect, session 
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, current_app
from datetime import datetime

from sqlalchemy import text


app = Flask(__name__)
app.secret_key = 'a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pl.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create database tables within the application context
with app.app_context():
    db.create_all()

# Import your routes here
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    expensename = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    paymode = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
   
# Base.metadata.create_all(engine)

#HOME--PAGE
@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/")
def add():
    return render_template("home.html")



#SIGN--UP--OR--REGISTER


# SIGN UP OR REGISTER
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if the username already exists
        
        user = User.query.filter_by(username=username).first()
        if user:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Name must contain only characters and numbers!'
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            msg = 'You have successfully registered!'
            return render_template('signup.html', msg=msg)
        
        return render_template('signup.html', msg=msg)
    


        
# LOGIN PAGE
@app.route("/signin")
def signin():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['loggedin'] = True
        session['id'] = user.id
        session['username'] = user.username
        return redirect('/home')
    else:
        msg = 'Incorrect username / password!'
        return render_template('login.html', msg=msg)



#ADDING----DATA


@app.route("/add")
def adding():
    return render_template('add.html')


@app.route("/addexpense", methods=['POST'])
def addexpense():
    date_str = request.form['date']
    date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')  # Adjust format string
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']
    
    # Create a new Expense object
    expense = Expense(
        user_id=session['id'],
        date=date_obj,  # Use the parsed date object
        expensename=expensename,
        amount=amount,
        paymode=paymode,
        category=category
    )
    
    # Add the new Expense object to the session
    db.session.add(expense)
    
    # Commit the session to persist the changes
    db.session.commit()
    
    return redirect("/display")



                          
@app.route("/display")
def display():
    user_id = session.get('id')
    if user_id is None:
        # Handle case where user is not logged in
        return redirect('/login')  # Redirect to login page or handle appropriately
    
    # Get current date in YYYY-MM-DD format
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Query expenses using SQLAlchemy ORM
    expenses = Expense.query.filter_by(user_id=user_id).filter(Expense.date <= current_date).order_by(Expense.date.desc()).all()
    
    # Calculate total expenses and category-wise totals
    total = sum(expense.amount for expense in expenses)
    t_edu = sum(expense.amount for expense in expenses if expense.category == 'edu')
    t_food = sum(expense.amount for expense in expenses if expense.category == 'food')
    t_entertainment = sum(expense.amount for expense in expenses if expense.category == 'entertainment')
    t_business = sum(expense.amount for expense in expenses if expense.category == 'business')
    t_rent = sum(expense.amount for expense in expenses if expense.category == 'rent')
    t_EMI = sum(expense.amount for expense in expenses if expense.category == 'EMI')
    t_other = sum(expense.amount for expense in expenses if expense.category == 'other')
    
    return render_template('display.html', expenses=expenses, total=total, t_edu = t_edu,
                           t_food=t_food, t_entertainment=t_entertainment,
                           t_business=t_business, t_rent=t_rent,
                           t_EMI=t_EMI, t_other=t_other)



#delete---the--data

@app.route('/delete/<string:id>', methods = ['POST', 'GET' ])
def delete(id):
     cursor = db.connection.cursor()
     cursor.execute('DELETE FROM expenses WHERE  id = {0}'.format(id))
     db.connection.commit()
     print('deleted successfully')    
     return redirect("/display")
 
    
#UPDATE---DATA

@app.route('/edit/<id>', methods = ['POST', 'GET' ])
def edit(id):
    cursor = db.connection.cursor()
    cursor.execute('SELECT * FROM expenses WHERE  id = %s', (id,))
    row = cursor.fetchall()
   
    print(row[0])
    return render_template('edit.html', expenses = row[0])




@app.route('/update/<id>', methods = ['POST'])
def update(id):
  if request.method == 'POST' :
   
      date = request.form['date']
      expensename = request.form['expensename']
      amount = request.form['amount']
      paymode = request.form['paymode']
      category = request.form['category']
    
      cursor = db.connection.cursor()
       
      cursor.execute("UPDATE `expenses` SET `date` = % s , `expensename` = % s , `amount` = % s, `paymode` = % s, `category` = % s WHERE `expenses`.`id` = % s ",(date, expensename, amount, str(paymode), str(category),id))
      db.connection.commit()
      print('successfully updated')
      return redirect("/display")
     
      
# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')
             

if __name__ == "__main__":
    app.run(debug=True)
    
    