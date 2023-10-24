from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from db import db


def get_all_permitted_users():
    permitted_teachers_sql = text("""
        SELECT github_handle, 'teacher' as role 
        FROM permitted_teachers 
        ORDER BY github_handle ASC
    """)
    permitted_students_sql = text("""
        SELECT github_handle, 'student' as role 
        FROM permitted_students 
        ORDER BY github_handle ASC
    """)
    teachers = db.session.execute(permitted_teachers_sql).fetchall()
    students = db.session.execute(permitted_students_sql).fetchall()
    return teachers + students


def get_pending_permission_requests():
    sql = text("""
        SELECT * 
        FROM permission_requests 
        WHERE status = 'pending'
    """)
    result = db.session.execute(sql)
    return result.fetchall()


def get_permission_request_status(github_handle):
    sql = text("""
        SELECT status 
        FROM permission_requests 
        WHERE github_handle = :github_handle
    """)
    result = db.session.execute(sql, {"github_handle": github_handle})
    request_status = result.fetchone()
    return request_status[0] if request_status else None


def is_permitted(github_handle, role):
    if role == "teacher":
        table_name = "permitted_teachers"
    else:
        table_name = "permitted_students"
    sql = text(f"""
        SELECT * 
        FROM {table_name} 
        WHERE github_handle = :github_handle
    """)
    result = db.session.execute(sql, {"github_handle": github_handle})
    return result.fetchone() is not None


def add_permitted_user(github_handle, role):
    table_name = "permitted_teachers" if role == "teacher" else "permitted_students"
    sql = text(f"""
        INSERT INTO {table_name} (github_handle) 
        VALUES (:github_handle)
    """)
    db.session.execute(sql, {"github_handle": github_handle})
    db.session.commit()

    delete_permission_request_sql = text("""
        DELETE FROM permission_requests 
        WHERE github_handle = :github_handle
    """)
    db.session.execute(delete_permission_request_sql, {"github_handle": github_handle})
    db.session.commit()


def delete_permitted_user(github_handle):
    for table_name in ["permitted_teachers", "permitted_students"]:
        sql = text(f"""
            DELETE FROM {table_name} 
            WHERE github_handle = :github_handle
        """)
        db.session.execute(sql, {"github_handle": github_handle})
    db.session.commit()


def add_permission_request(github_handle, requested_role):

    if is_permitted(github_handle, "teacher") or is_permitted(github_handle, "student"):
        raise Exception(f"{github_handle} is already permitted. Cannot make a new permission request.")

    existing_status = get_permission_request_status(github_handle)
    if existing_status:
        raise Exception(f"Permission request for {github_handle} already exists with status {existing_status}")

    try:
        sql = text("""
            INSERT INTO permission_requests (github_handle, requested_role, status) 
            VALUES (:github_handle, :requested_role, 'pending')
        """)
        db.session.execute(sql, {"github_handle": github_handle, "requested_role": requested_role})
        db.session.commit()
    except Exception as e:
        raise Exception(f"Error adding permission request")


def update_request_status(request_id, status):
    sql = text("""
        UPDATE permission_requests 
        SET status = :status 
        WHERE id = :id
    """)
    db.session.execute(sql, {"status": status, "id": request_id})
    db.session.commit()
