from flask import Flask, render_template, request,flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import pickle
import bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/mydatabase'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class Mydatabase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

##############


#########


    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))





with app.app_context():
    db.create_all()

@app.route('/')
def indexss():
    return render_template('indexss.html')


#   ########      this code modify

"""@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = Mydatabase(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')"""
#####################


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if the email already exists in the database
        existing_user = Mydatabase.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists. Please log in.')
            return redirect('/login')

        # If the email doesn't exist, proceed with registration
        new_user = Mydatabase(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')
    
    
    
     
    
############################    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Mydatabase.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/index')
        else:
            return render_template('login.html', error='Invalid user')

    return render_template('login.html')

try:
    popular_df = pickle.load(open('templates/popular (3).pkl', 'rb'))
    pt = pickle.load(open('templates/pt.pkl', 'rb'))
    books = pickle.load(open('templates/books (1).pkl', 'rb'))
    similarity_scores = pickle.load(open('templates/similarity_scores.pkl', 'rb'))
except FileNotFoundError as e:
    print(f"Error loading pickled data: {e}")
    popular_df, pt, books, similarity_scores = None, None, None, None

@app.route('/index')
def index():
    if 'email' in session:
        user = Mydatabase.query.filter_by(email=session['email']).first()
        return render_template('index.html',
                               book_name=list(popular_df['Book-Title'].values),
                               author=list(popular_df['Book-Author'].values),
                               image=list(popular_df['Image-URL-M'].values),
                               votes=list(popular_df['num_ratings'].values),
                               rating=list(popular_df['avg_rating'].values))
    #return redirect('/login')

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    try:
        user_input = request.form.get('user_input')
        if user_input is None or pt is None or books is None or similarity_scores is None:
            return "Error: Data not available or invalid input."

        if user_input not in pt.index:
            error_message = "Error: User input not found in index."
            ######## tumi judi recommend.html cao tahole tata.html dio na 
            ######## recommend.html dite error asbe na sekhane bar bar recommend.html asbe  
            return render_template('it_not.html', error=error_message)
        
        index = np.where(pt.index == user_input)[0]
        if len(index) == 0:
            return "Error: User input not found in index."

        index = index[0]  # Use the first index if multiple matches exist

        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:10]

        data = []
        for i in similar_items:
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            if not temp_df.empty:
                item = [
                    temp_df['Book-Title'].values[0],
                    temp_df['Book-Author'].values[0],
                    temp_df['Image-URL-M'].values[0]
                ]
                data.append(item)

        print(data)
        return render_template('recommend.html', data=data)

    except Exception as e:
        print(f"Error in recommend route: {e}")
        return "An error occurred."
########## 
 
    
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message
        
        
            
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()
        return redirect('/thank_you')

    return render_template('contact.html')

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')




if __name__ == '__main__':
    app.run(debug=True,port=2020)
