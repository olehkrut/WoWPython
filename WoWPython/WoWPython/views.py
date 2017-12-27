"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import Flask, render_template, session, jsonify, request
from WoWPython import app

from flask_sqlalchemy import SQLAlchemy

import sqlalchemy
import json
from sqlalchemy.ext.serializer import loads, dumps

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/register', methods=('POST',))
def register():
    if 'username' not in request.form or 'email' not in request.form or 'password' not in request.form:
        return 'Missing parameters', 400
    user = dbsession.query(User).filter(User.username == request.form['username']).first()
    if not user:
        user = User(username=request.form['username'], password=request.form['password'], email=request.form['email'])
        dbsession.add(user)
        dbsession.commit()
        session['username'] = request.form['username']
        return '', 204
    return 'User already exists', 400


@app.route('/login', methods=('POST',))
def login():
    if 'username' not in request.form or 'password' not in request.form:
        return 'Missing parameters', 400
    user = dbsession.query(User).filter(User.username == request.form['username']).first()
    if user.password != request.form['password']:
        return 'Username or password is not valid', 400
    session['username'] = request.form['username']
    return '', 204


@app.route('/logout', methods=('POST',))
def logout():
    session.pop('username')
    return '', 204


@app.route('/account', methods=('POST',))
def add_account():
    if 'username' in session:
        user = dbsession.query(User).filter(User.username == session['username']).first()
        account = Account(name=request.form['name'], user_id=user.id)
        dbsession.add(account)
        dbsession.commit()
        return '', 204
    return 'Unauthorized', 401

@app.route('/account/<id>')
def get_account(id):
    if 'username' not in session:
        return 'Unauthorized', 401
    account = dbsession.query(Account).filter(Account.id == id).first()
    if not account:
        return 'account missing', 400
    user = dbsession.query(User).filter(User.username == session['username']).first()
    account_members = dbsession.query(AccountMember).join(User).filter(AccountMember.account_id == account.id).all()
    member = [m for m in account_members if m.user_id == user.id]
    if account.user_id != user.id and not member:
        return 'user not in account', 400
    transactions = [{
        'id': i.id,
        'name': i.name,
        'amount': i.amount
    } for i in dbsession.query(Transaction).filter(Transaction.account_id == id).all()]
    return json.dumps({
        'account': {
            'id': id,
            'name': account.name,
            'owner': account.user_id == user.id
        },
        'users': [{
            'username': m.user.username
        } for m in account_members],
        'transactions': transactions
    })


@app.route('/account', methods=('PUT',))
def update_account():
    if 'username' not in session:
        return 'Unauthorized', 401
    id = request.form['id']
    account = dbsession.query(Account).filter(Account.id == id).first()
    if not account:
        return 'account missing', 400
    user = dbsession.query(User).filter(User.username == session['username']).first()
    if account.user_id != user.id:
        return 'account missing', 400
    account.name = request.form['name']
    dbsession.commit()
    return '', 204


@app.route('/account', methods=('DELETE',))
def delete_account():
    if 'username' not in session:
        return 'Unauthorized', 401
    id = request.form['id']
    account = dbsession.query(Account).join(User).filter(Account.id == id and User.username == session['username']).first()
    if not account:
        return 'account missing', 400
    dbsession.query(AccountMember).filter(AccountMember.account_id == id).delete()
    dbsession.query(Transaction).filter(Transaction.account_id == id).delete()
    dbsession.delete(account)
    dbsession.commit()
    return '', 204


@app.route('/account_member', methods=('POST',))
def account_member_add():
    '''
    Add user to account
    id - account id
    username - user name
    '''
    if 'username' not in session:
        return 'Unauthorized', 401
    account = dbsession.query(Account).join(User).filter(User.username == session['username'] and Account.id == request.form['id']).first()
    if not account:
        return 'account missing', 400
    user = dbsession.query(User).filter(User.username == request.form['username']).first()
    if not user or user.username == session['username']:
        return 'user missing', 400
    account_member = AccountMember(user_id=user.id, account_id=account.id)
    dbsession.add(account_member)
    dbsession.commit()
    return jsonify({
        'id': user.id,
        'name': user.username
    })


@app.route('/account_member', methods=('DELETE',))
def account_member_remove():
    '''
    Remove user from account
    Params:
    id - account id
    userId - user id
    '''
    if 'username' not in session:
        return 'Unauthorized', 401
    account = dbsession.query(Account).join(User).filter(User.username == session['username'] and Account.id == request.form['id']).first()
    if not account:
        return 'account missing', 400
    dbsession.query(AccountMember).filter(AccountMember.user_id == request.form['userId'] and AccountMember.account_id == request.form['id']).delete()
    dbsession.commit()
    return '', 204


@app.route('/add_transaction', methods=('POST',))
def add_transaction():
    if 'username' not in session:
        return 'Unauthorized', 401
    transaction = Transaction(name=request.form['name'], amount=request.form['amount'], account_id=request.form['account_id'])
    dbsession.add(transaction)
    dbsession.commit()
    return '', 204



@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
