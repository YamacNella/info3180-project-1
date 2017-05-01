"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, jsonify, json, send_from_directory, make_response, abort
from flask_login import login_user, logout_user, current_user, login_required
from forms import registerForm, loginForm, wishlistForm, shareForm
from models import Profiles, Wishlist, users_wishes
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.sql import text
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
import requests
import urlparse
import time
import os
import random
import datetime 
import smtplib

app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(seconds = 86400) # token expires in timedelta
app.config['JWT_AUTH_ENDPOINT'] = 'bearer' # Authorization header
app.config['JWT_AUTH_HEADER_PREFIX'] = 'BEARER' # OAuth2 Bearer tokens

def authenticate(email,password):
    """ Returns an authenticated identity """
    user = Profiles.query.filter_by(email=email).first()
    if not user:
        abort(404) 
    if user.check_password(password):
        return user
    else:
        abort(401)

def identity(payload):
    """ Returns a user given an existing token """
    return Profiles.query.get(payload['identity'])
    
def auth_response_handler(access_token, identity):
    """ Custom token response """
    err = None
    msg = "Success"
    userData = {'email': identity.email, 'name': identity.name}
    jsonData = {'user': userData, 'access_token': access_token.decode('utf-8'), 'payload': jwt.jwt_payload_callback(identity)}
    return jsonify(error=err, data=jsonData, message=msg)

## Setup Flask-JWT
jwt = JWT(app, authenticate, identity)

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')

@app.route("/api/users/register", methods=["GET","POST"])
def register():
    """ Registers a new user """
    form = registerForm()
    if request.method == "POST":
        if form.validate_on_submit():
            name = request.form['name']
            username = request.form['username']
            email = request.form['email']
            password = form.password.data
            age = request.form['age']
            imageFolder = app.config["UPLOAD_FOLDER"]
           
            imageFile = request.files['image']
            if imageFile.filename == '':
                imageName = "cats.jpg" 
            else:
                imageName = secure_filename(imageFile.filename)
                imageFile.save(os.path.join(imageFolder, imageName))
            
            while True:
                userid = (random.randint(100, 100000))
                result = Profiles.query.filter_by(userid=userid).first() 
                if result is None:
                    break
                
            profile_added_on = timeinfo()
            
            user = Profiles(userid, username, name, age, imageName, email, password, profile_added_on)
            db.session.add(user)
            db.session.commit()

            err = False
            msg = "Success"
            userData = {'email': user.email,'name': user.name, 'password': user.password, 'age': user.age, 'image': user.image}
            return redirect("wishlist", userid=current_user.get_id())
        else:
            err = True
            msg = form.errors
            userData = None
        
        return jsonify(error=err, data=userData, message=msg)
                        
    flash_errors(form)
    return render_template("register.html", form=form)

@app.route("/api/users/login", methods=["GET", "POST"])
def login():
    """ Accepts login credentials as email and password """
    form = loginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
              
            user = Profiles.query.filter_by(email=email, password=password).first()
           
            if user is not None:
                login_user(user)
                flash("You made it in!", 'success')
                
                err = False
                msg = "Success"
                userData = {'email': user.email, 'password': user.password}
                return redirect(url_for("home"))
            
            else:
                flash('Email or Password incorrect.', 'danger')
                err = True
                msg = "Invalid email/password"
                userData = user
        else:
            err = True
            userData = None
            msg = form.errors
        jsonify(error=err, data=userData, message=msg)
        
    flash_errors(form)
     
    return render_template("login.html", form=form)


@login_manager.user_loader
def load_user(userid):
    return Profiles.query.get(userid)

@app.route("/api/users/<userid>/wishlist", methods=["GET","POST"])
def wishlist(userid):
    """ Renders user's wishlist """
    user = db.session.query(Profiles).filter_by(userid=userid).first()
    
    if request.method == "GET": #VIEW
        if user:
            wishList = []
            query = text("""SELECT Wishlist.itemid, Wishlist.title, Wishlist.description, Wishlist.url, Wishlist.thumbnailurl FROM Wishlist INNER JOIN users_wishes ON users_wishes.wishid = Wishlist.itemid WHERE users_wishes.userid = :userid""")
            wishes = db.session.get_bind().execute(query, userid = user.userid)
            
            if wishes:
                for wish in wishes:
                    wishDict = {'id': wish["itemid"], 'title': wish["title"], 'description': wish["description"], 'url': wish["url"], 'thumbnailurl': wish["thumbnailurl"]}
                    wishList.append(wishDict)

                err = None
                msg = "Success"
                userData = {"items": wishList}
                return  render_template("viewwishlist.html")
            else:
                err = True
                msg = "No wishes found"
                userData = {"items": wishList}
                return  render_template("viewwishlist.html")
        else: 
            abort(404)
        
        return jsonify(error=err, data=userData, message=msg)
                
    elif request.method == "POST":
        render_template("addtowishlist.html") #ADD
    
        if request.json:
            jsonObj = request.json
        else:
            abort(400) #BAD REQUEST

        if 'title' not in jsonObj or 'description' not in jsonObj or 'url' not in jsonObj or 'thumbnailurl' not in jsonObj:
            abort(400) #MISSING DATA
       
        title = jsonObj['title']
        description = jsonObj['description']
        url = jsonObj['url']
        thumbnailurl = jsonObj['thumbnail']
        
        if user:
            # Create Wish object
            wish = Wishlist(title,description,url,thumbnailurl)
            db.session.add(wish)
            db.session.commit()
            db.session.get_bind().execute(users_wishes.insert(), user_id=userid, wish_id=wish.itemid)
            
            err = None
            itemData = {'id': wish.item_id, 'title': wish.title, 'description': wish.description, 'url': wish.url, 'thumbnailurl': wish.thumbnailurl, 'uri': url_for('get_item', itemid = wish.item_id, _external = True)}
            msg = "Success"
        else:
            abort(404)
        return jsonify(error=err, data={'item': itemData}, message=msg), 201 #CREATED

@app.route('/api/thumbnails', methods=['GET'])
def get_thumbnails(url):
    """ Thumbnais """
    if not request.json or 'url' not in request.json:
        abort(400)
    url = request.json['url']
    urls = get_imageURLS(url)
    if urls:
        err = None
        msg = "Success"
    else:
        err = "Request Error"
        msg = "Failed"
    return jsonify(error=err, data={'thumbnails': urls}, message=msg)

@app.route("/api/users/<userid>/wishlist/<itemid>", methods=["DELETE"])
@jwt_required()
@login_required
def delete_item(userid, itemid):
    """ Deletes an item from wishlist """
    user = db.session.query(Profiles).filter_by(userid=userid).first()
    if user:
        wish = db.session.query(Wishlist).filter_by(itemid=itemid).first()
        if wish:
            db.session.delete(wish)
            db.session.commit()

            err = None
            msg = "Success"
            userData = {'itemid': wish.itemid, 'title': wish.title}
        else:
            err = True
            msg = "Wish Item not found"
            userData = {}
    else:
        err = True
        msg = "User not found"
        userData = None
    return jsonify(error=err, data=userData, message=msg) 

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You are logged out', 'danger')
    return redirect(url_for('home'))

@app.route('/api/user/<int:userid>/wishlist/share', methods=['POST'])
def share(userid):
    form = shareForm()
    user = db.session.query(Profiles).filter_by(userid = userid).first()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            email = request.form['email']
            
            name = user.name
            sender = user.email

            subject = "Hey! Look at my Wishlist"
            
            link = "http://"+ app.config['host'] + "/" + str(app.config['port']) + "/api/user/" + userid + "/wishlist"
            message = "Hey check out my wishlist! " + "" + link
    
            sendemail(email, sender, name, subject, message) 
            err = None
            userData = email
            msg = "Wishes shared!"
            return jsonify(error = err, data = userData, message = msg)
            
    return render_template('share.html', form=form)
   
   
@app.route('/api/user/<int:userid>/wishlist/shared', methods=['GET'])
@login_required
def shared(userid):
    user = db.session.query(Profiles).filter_by(userid = userid).first()
    wishlistItems = db.session.query(Wishlist).filter_by(userid=userid).all()
    if wishlistItems is None or user is None:
        err = True
        msg = "No wishlist exists"
        userData = {}
        return jsonify(error = err, data = userData, message = msg)
    
    wishes = []    
    for wish in wishlistItems:
        wishes.append({"title":wish.title, "description":wish.description, "url":wish.url, "thumbnailurl":wish.thumbnailurl})
    
    err = None
    userData = wishes
    msg = "Success"
    return jsonify(error = err, data = userData, message = msg)    

###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

def timeinfo():
    """ Returns the current datetime """
    return time.strftime("%d %b %Y")

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (getattr(form, field).label.text, error), 'something is not right')

def get_imageURLS(url):
    """ Returns a list of thumbnail URLS """
    result = requests.get(url)
    soup = BeautifulSoup(result.text, "html.parser")

    og_image = (soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'og:image'}))
    if og_image and og_image['content']:
        pass

    thumbnail_spec = soup.find('link', rel='image_src')
    if thumbnail_spec and thumbnail_spec['href']:
        pass

    imgs = [] 
    for img in soup.findAll("img", src=True):
        
        imgs.append(urlparse.urljoin(url, img["src"]))
    return imgs

@app.route('/img/<path:filename>')
def serve_file(filename):
    dir = app.config["UPLOADS_FOLDER"]
    return send_from_directory(dir,filename)

def sendemail(email, sender, name, subject, msg):
    """Send's user's shared wishlist"""
    message = """From: {} <{}>\nTo: {} <{}>\nSubject: {}\n\n{}"""
    # Format message to be sent
    message_to_send = message.format(name, sender, email, email, subject, msg)

    server = smtplib.SMTP('localhost')
    server.sendmail(sender, email, message_to_send)
    server.quit()
    return


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
