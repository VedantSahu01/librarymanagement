from flask import Flask, request, render_template, redirect,request, session, url_for
import pymongo
import hashlib


app = Flask(__name__, static_folder="static")
app.secret_key = 'any random string'
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["library"]
libDB =db.librarianDB
stuDB =db.StudentDB
bookDB =db.bookDB

# Home page to login as Admin or Librarian
@app.route('/',methods = ['GET','POST'])
def home():
    return render_template('index.html')

# Login for admin and librarian
@app.route('/adminLogin', methods= ['POST'])
def admin_login():
    if 'username' and 'password' in session:
        if session['type'] == '1':
            return redirect(url_for('admin'))
    session.pop('username', None)
    session.pop('password', None)
    session.pop('type', None)
    return render_template('login.html',title="Admin Login",type='1')
@app.route('/librarianLogin', methods= ['POST'])
def librarian_login():
    if 'username' and 'password' in session:
        if session['type'] == '2':
            return redirect(url_for('librarian'))
    session.pop('username', None)
    session.pop('password', None)
    session.pop('type', None)
    return render_template('login.html',title="Librarian login",type='2')

# Dashboard for Admin/Librarian
@app.route('/admin', methods = ['GET'])
def admin():
    if 'username' and 'password' in session:
        if session['type'] == '1':
            return render_template('admin.html')
    return redirect(url_for('home'))
@app.route('/librarian', methods = ['GET'])
def librarian():
    if 'username' and 'password' in session:
        if session['type'] == '2':
            return render_template('librarian.html')
    return redirect(url_for('home'))

#Authorise
@app.route('/auth', methods= ['POST'])
def authorize():
    if request.form['type'] == '1':
        if request.form['id'] == 'admin@mail.com' and request.form['pass'] == 'administrator':
            session['username'] = 'admin@mail.com'
            session['password'] = 'administator'
            session['type'] = '1'
            return redirect(url_for('admin'))
        return render_template('login.html',title="Admin login",type='1',err="Invalid username/password")
    if request.form['type'] == '2':
        password = request.form['pass']
        h = hashlib.md5(password.encode())
        libDetails = libDB.find_one({"email":request.form['id'] , "password":h.hexdigest()})
        if libDetails:
            session['username'] = request.form['id']
            session['password'] = request.form['pass']
            session['type'] = '2'
            return redirect(url_for('librarian'))
        return render_template('login.html',title="Librarian login",type='2',err="Invalid username/password")

#Admin Dashboard Operations
# - add
@app.route('/admin/add',methods=['POST','GET'])
def addLibrarian():
    if 'username' and 'password' in session:
        if session['type'] == '1':
            return render_template('addLibrarian.html')
    return redirect(url_for('home'))
@app.route('/admin/added',methods=['POST'])
def addedLibrarian():
    password = request.form['pass']
    h = hashlib.md5(password.encode())
    lib = libDB.find_one({'email': request.form['id']})
    if not lib:
        libDB.insert_one({
            "handle": request.form['handle'],
            "email": request.form['id'],
            "password": h.hexdigest()  ,
        })
        return "Successfully added librarian to DB"
    return redirect(url_for('addLibrarian'))
# - view
@app.route('/admin/view',methods=['POST'])
def viewLibrarian():
    if 'username' and 'password' in session:
        if session['type'] == '1':
            allLib = libDB.find()
            return render_template('viewLibrarian.html',all = allLib)
    return redirect(url_for('home'))
# - delete
@app.route('/admin/delete',methods=['POST','GET'])
def deleteLibrarian():
    if 'username' and 'password' in session:
        if session['type'] == '1':
            return render_template('deleteLibrarian.html')
    return redirect(url_for('home'))
@app.route('/admin/deleted',methods=['POST'])
def deletedLibrarian():
    lib = libDB.find_one({"email":request.form['email']})
    if lib:
        libDB.delete_one({"email":request.form['email']})
        return 'Librarian deleted from DB'
    return redirect(url_for("deleteLibrarian"))

# Librarian dashboard operations
# - add student
@app.route('/librarian/add',methods=['POST','GET'])
def addStudent():
    if 'username' and 'password' in session:
        if session['type'] == '2':
            return render_template('addStudent.html')
    return redirect(url_for('home'))
@app.route('/librarian/added',methods=['POST'])
def addedStudent():
    stu = stuDB.find_one({'roll':request.form['roll']})
    if not stuDB:
        stuDB.insert_one({
            "handle": request.form['handle'],
            "email": request.form['id'],
            "roll": request.form['roll'],
            "books": [],
        })
        return 'Student added to DB'
    return redirect(url_for('addStudent'))
# - view student
@app.route('/librarian/view',methods=['POST'])
def viewStudent():
    if 'username' and 'password' in session:
        if session['type'] == '2':
            allStu = stuDB.find()
            return render_template('viewStudent.html',all = allStu)
    return redirect(url_for('home'))
# - delete student
@app.route('/librarian/delete',methods=['POST','GET'])
def deleteStudent():
    if 'username' and 'password' in session:
        if session['type'] == '2':
            return render_template('deleteStudent.html')
    return redirect(url_for('home'))
@app.route('/librarian/deleted',methods=['POST'])
def deletedStudent():
    stu = stuDB.find_one({"email":request.form['email']})
    if stu:
        stuDB.delete_one({"email":request.form['email']})
        return 'Student deleted from DB'
    return redirect(url_for('deleteStudent'))
# - add book
@app.route('/librarian/addBook',methods=['POST','GET'])
def addBook():
    if 'username' and 'password' in session:
        if session['type'] == '2':
            return render_template('addBook.html')
    return redirect(url_for('home'))
@app.route('/librarian/addedBook',methods=['POST'])
def addedBook():
    book = bookDB.find_one({"name": request.form['name']})
    if not book:
        bookDB.insert_one({
            "name": request.form['name'],
            "author": request.form['author'],
            "issued": False,
        })
        return 'Book added to DB'
    return redirect(url_for('addBook'))
# - view books
@app.route('/librarian/viewBooks',methods=['POST'])
def viewBook():
    if 'username' and 'password' in session:
        if session['type'] == '2':
            allBook = bookDB.find()
            return render_template('viewBook.html',all = allBook)
    return redirect(url_for('home'))
# - issue book
@app.route('/librarian/issue',methods=['POST'])
def issueBook():
    if 'username' and 'password' in session:
        if session['type'] == '2':
            return render_template('issueBook.html')
    return redirect(url_for('home'))
@app.route('/librarian/issued', methods=['POST'])
def issuedBook():
    student = stuDB.find_one({'roll': request.form['roll']})
    book = bookDB.find_one({'name': request.form['name']})
    if student and book:
        bookDB.update_one({'name':request.form['name']},{"$set":{"issued": True}})
        stuDB.update_one({'roll': request.form['roll']},{"$push":{"books": request.form['name']}})
        return 'Book issued'
    return render_template('issueBook.html')
# - view issued books
@app.route('/librarian/viewissue',methods=['POST'])
def viewissue():
    if 'username' and 'password' in session:
        if session['type'] == '2':
            issuedbooks = stuDB.find({'books': { '$exists': True,'$not': { '$size': 0}}})
            return render_template('viewIssuedBooks.html',all =issuedbooks)
    return redirect(url_for('home'))
# - return book
@app.route('/librarian/return',methods=['POST'])
def returnBook():
    if 'username' and 'password' in session:
        if session['type'] == '2':
            return render_template('returnBook.html')
    return redirect(url_for('home'))
@app.route('/librarian/returned', methods=['POST'])
def returnedBook():
    student = stuDB.find_one({'roll': request.form['roll'],'books': request.form['name']})
    book = bookDB.find_one({'name': request.form['name']})
    if student and book:
        bookDB.update_one({'name':request.form['name']},{"$set":{"issued": False}})
        stuDB.update_one({'roll': request.form['roll']},{"$pull":{"books": request.form['name']}})
        return 'Book returned to library'
    return render_template('returnBook.html')

# Logout operation for admin/librarian
@app.route('/logout' , methods=['POST'])
def logout():
    session.pop('username', None)
    session.pop('password', None)
    session.pop('type', None)
    return 'Successfully LoggedOut'

# url_for('static', filename='styles.css')
