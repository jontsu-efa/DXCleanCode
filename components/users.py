import os
from flask import abort, request, session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from db import db
from components import permissions


def get_all_users():
    sql = text("""
        SELECT * 
        FROM users
    """)
    result = db.session.execute(sql)
    return result.fetchall()


def get_user_by_github_handle(github_handle):
    try:
        sql = text("""
            SELECT * 
            FROM users 
            WHERE github_handle = :github_handle
        """)
        result = db.session.execute(sql, {"github_handle": github_handle})
        user = result.fetchone()
        return user
    except Exception as e:
        raise Exception(f"Error fetching user details: {str(e)}")


def register_user(github_handle, password):
    if not get_all_users():
        role = "teacher"
        permissions.add_permitted_user(github_handle, role)
    else:
        if permissions.is_permitted(github_handle, "teacher"):
            role = "teacher"
        elif permissions.is_permitted(github_handle, "student"):
            role = "student"
        else:
            permission_status = permissions.get_permission_request_status(github_handle)
            if permission_status == "pending":
                raise Exception("Your permission request is pending. Please try again tomorrow or contact your teacher.")
            elif permission_status == "rejected":
                raise Exception("Your permission request has been rejected. Please contact your teacher.")
            else:
                raise Exception("GitHub handle not permitted. Please request permission.")
    
    hashed_password = generate_password_hash(password)
    try:
        sql = text("""
            INSERT INTO users (github_handle, password, role) 
            VALUES (:github_handle, :password, :role)
        """)
        db.session.execute(sql, {"github_handle": github_handle, "password": hashed_password, "role": role})
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception("Github handle already exists.")
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error registering user: {str(e)}")
    

def login_user(github_handle, password):
    user_data = get_user_by_github_handle(github_handle)

    if not user_data or not permissions.is_permitted(user_data[1], user_data[3]):
        raise Exception("Invalid credentials")

    try:
        sql = text("""
            SELECT password 
            FROM users 
            WHERE github_handle = :github_handle
        """)
        result = db.session.execute(sql, {"github_handle": github_handle})
        user = result.fetchone()

        if user and check_password_hash(user[0], password):
            session["user_id"] = user_data[0]
            session["github_handle"] = github_handle
            session["role"] = user_data[3]
            session["csrf_token"] = get_or_create_csrf_token()
            return True
        
        return False
    except Exception as e:
        raise Exception(f"Error logging in: {str(e)}")


def logout_user():
    keys_to_delete = ["user_id", "github_handle", "role", "csrf_token"]
    for key in keys_to_delete:
        try:
            del session[key]
        except KeyError:
            pass


def get_or_create_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = os.urandom(16).hex()
    return session["csrf_token"]


def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
