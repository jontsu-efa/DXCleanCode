from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from db import db


def get_all_exercises():
    sql = text("""
        SELECT * 
        FROM exercises
    """)
    result = db.session.execute(sql)
    exercises = result.fetchall()
    return exercises


def get_exercise_by_id(exercise_id):
    sql = text("""
        SELECT * 
        FROM exercises 
        WHERE id = :exercise_id
    """)
    result = db.session.execute(sql, {"exercise_id": exercise_id})
    exercise = result.fetchone()
    return exercise


def get_creator_of_exercise(exercise_id):
    sql = text("""
        SELECT u.* 
        FROM users u 
        JOIN exercises e ON u.id = e.creator_id 
        WHERE e.id = :exercise_id
    """)
    result = db.session.execute(sql, {"exercise_id": exercise_id})
    user = result.fetchone()
    return user


def create_exercise(name, tasks, creator_id):
    try:
        sql = text("""
            INSERT INTO exercises (name, tasks, creator_id) 
            VALUES (:name, :tasks, :creator_id)
        """)
        db.session.execute(sql, {"name": name, "tasks": tasks, "creator_id": creator_id})
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception("Exercise name already exists")
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error creating exercise: {str(e)}")


def update_exercise(exercise_id, name, tasks):
    try:
        sql = text("""
            UPDATE exercises 
            SET name = :name, tasks = :tasks 
            WHERE id = :exercise_id
        """)
        db.session.execute(sql, {"exercise_id": exercise_id, "name": name, "tasks": tasks})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error updating exercise: {str(e)}")


def delete_exercise(exercise_id, creator_id):
    try:
        sql = text("""
            DELETE FROM exercises 
            WHERE id = :exercise_id AND creator_id = :creator_id
        """)
        result = db.session.execute(sql, {"exercise_id": exercise_id, "creator_id": creator_id})
        db.session.commit()

        if result.rowcount == 0:
            return False
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error deleting exercise: {str(e)}")
