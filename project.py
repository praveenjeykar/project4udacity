from flask import (Flask,
                   render_template,
                   request, redirect,
                   jsonify, url_for, flash)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Gun, GunModel, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Gun Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///gundatabase.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    session = DBSession()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    session.close()
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    session = DBSession()
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        session.close()
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                   json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
    -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    session.close()
    return output

# User Helper Functions


def createUser(login_session):
    session = DBSession()
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    session.close()
    return user.id


def getUserInfo(user_id):
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    session.close()
    return user


def getUserID(email):
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=email).one()
        session.close()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    session = DBSession()
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        session.close()
        return response


# JSON APIs to view Restaurant Information
@app.route('/guncompany/<int:guncompany_id>/menu/JSON')
def guncompanyMenuJSON(guncompany_id):
    session = DBSession()
    guncompany = session.query(Gun).filter_by(id=guncompany_id).one()
    items = session.query(GunModel).filter_by(
        guncompany_id=guncompany_id).all()
    session.close()
    return jsonify(GunModels=[i.serialize for i in items])


@app.route('/guncompany/<int:guncompany_id>/menu/<int:menu_id>/JSON')
def gunModelJSON(guncompany_id, menu_id):
    session = DBSession()
    Menu_Item = session.query(GunModel).filter_by(id=menu_id).one()
    session.close()
    return jsonify(Menu_Item=Menu_Item.serialize)


@app.route('/guncompany/JSON')
def guncomapanysJSON():
    session = DBSession()
    guncompanys = session.query(Gun).all()
    session.close()
    return jsonify(guncompanys=[r.serialize for r in guncompanys])


# Show all gun companys
@app.route('/')
@app.route('/guncompany/')
def showGuns():
    session = DBSession()
    guncompanys = session.query(Gun).order_by(asc(Gun.name))
    if 'username' not in login_session:
        session.close()
        return render_template('publicguncompanys.html',
                               guncompanys=guncompanys)
    else:
        return render_template('guncompanys.html', guncompanys=guncompanys)


# Create a new gun company


@app.route('/guncompany/new/', methods=['GET', 'POST'])
def newGun():
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGun = Gun(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newGun)
        flash('New Gun Company %s Successfully Created' % newGun.name)
        session.commit()
        session.close()
        return redirect(url_for('showGuns'))
    else:
        return render_template('newGun.html')

# Edit a gun company


@app.route('/guncompany/<int:guncompany_id>/edit/', methods=['GET', 'POST'])
def editGun(guncompany_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    editedGun = session.query(Gun).filter_by(id=guncompany_id).one()
    if request.method == 'POST':
        editedGun.name = request.form['name']
        session.add(editedGun)
        flash('Gun Successfully Edited %s' % request.form['name'])
        session.commit()
        session.close()
        return redirect(url_for('showGuns'))
    else:
        return render_template('editGun.html', guncompany=editedGun)
    if editedGun.user_id != login_session['user_id']:
	return "<html><script>alert('you are not allowed to edit this\
        restaurant.Please create your own restaurant to\
        edit.');</script></html>"


# Delete a gun company
@app.route('/guncompany/<int:guncompany_id>/delete/', methods=['GET', 'POST'])
def deleteGun(guncompany_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    guncompanyToDelete = session.query(
        Gun).filter_by(id=guncompany_id).one()
    if request.method == 'POST':
        session.delete(guncompanyToDelete)
        flash('%s Successfully Deleted' % guncompanyToDelete.name)
        session.commit()
        session.close()
        return redirect(url_for('showGuns', guncompany_id=guncompany_id))
    else:
        return render_template('deleteGun.html', guncompany=guncompanyToDelete)

    if guncompanyToDelete.user_id == login_session['user_id']:
	return "<script>function myFunction(){alert('you are not allowed to\
        delete this guncompany.Please create your own guncompany to\
        delete.');}</script><bodyonload='myFunction()''>"

# Show all gun models


@app.route('/guncompany/<int:guncompany_id>/')
@app.route('/guncompany/<int:guncompany_id>/menu/')
def showMenu(guncompany_id):
    session = DBSession()
    guncompany = session.query(Gun).filter_by(id=guncompany_id).one()
    creator = getUserInfo(guncompany.user_id)
    items = session.query(GunModel).filter_by(guncompany_id=guncompany_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        session.close()
        return render_template('publicarms.html',
                               items=items, guncompany=guncompany,
                               creator=creator)
    else:
        return render_template('main.html',
                               items=items, guncompany=guncompany,
                               creator=creator)


# Create a new gun model
@app.route('/guncompany/<int:guncompany_id>/menu/new/',
           methods=['GET', 'POST'])
def newGunModel(guncompany_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    guncompany = session.query(Gun).filter_by(id=guncompany_id).one()
    if request.method == 'POST':
        newItem = GunModel(name=request.form['name'],
                           description=request.form['description'],
                           price=request.form['price'],
                           course=request.form['course'],
                           guncompany_id=guncompany_id,
                           user_id=guncompany.user_id)
        session.add(newItem)
        flash('New Gun %s Model Successfully Created' % (newItem.name))
        session.commit()
        session.close()
        return redirect(url_for('showMenu', guncompany_id=guncompany_id))
    else:
        return render_template('Newgunmodel.html', guncompany_id=guncompany_id)
    if login_session['user_id'] != guncompany.user_id:
	return "<script>function myFunction() {alert('You are not authorized to\
        add menu items to this gun model. Please create your own gun\
        model to add items.');}</script><body onload='myFunction()''>"

# Edit a gun model


@app.route('/guncompany/<int:guncompany_id>/menu/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editGunModel(guncompany_id, menu_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(GunModel).filter_by(id=menu_id).one()
    guncompany = session.query(Gun).filter_by(id=guncompany_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit()
        flash('Gun Model Successfully Edited')
        session.close()
        return redirect(url_for('showMenu', guncompany_id=guncompany_id))
    else:
        return render_template('Editgunmodel.html',
                                guncompany_id=guncompany_id,
                                menu_id=menu_id, item=editedItem)
    if login_session['user_id'] != guncompany.user_id:
	return "<script>function myFunction() {alert('You are not authorized to\
        edit to this gun model. Please create your own gun model\
        to edit items.');}</script><body onload='myFunction()''>"


# Delete a gun model
@app.route('/guncompany/<int:guncompany_id>/menu/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def deleteGunModel(guncompany_id, menu_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    guncompany = session.query(Gun).filter_by(id=guncompany_id).one()
    itemToDelete = session.query(GunModel).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Gun Model Successfully Deleted')
        session.close()
        return redirect(url_for('showMenu', guncompany_id=guncompany_id))
    else:
        return render_template('Deletegunmodel.html', item=itemToDelete)
    if login_session['user_id'] != guncompany.user_id:
	return "<script>function myFunction() {alert('You are not authorized to\
        delete this gun model. Please create your own gun model\
        to delete items.');}</script><body onload='myFunction()''>"

if __name__ == '__main__':
        app.secret_key = 'super_secret_key'
        app.debug = True
        app.run(host='0.0.0.0', port=5000)
