from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from db import db


def get_solution_by_user_and_exercise(user_id, exercise_id):
    sql = text("""
        SELECT * 
        FROM solutions 
        WHERE submitter_id = :user_id 
        AND exercise_id = :exercise_id
    """)
    result = db.session.execute(sql, {"user_id": user_id, "exercise_id": exercise_id})
    solution_data = result.fetchone()
    return solution_data


def submit_or_update_solution(exercise_id, submitter_id, solution_link, comment_link_1=None, comment_link_2=None, comment_link_3=None):
    try:
        sql = text("""
            INSERT INTO solutions (solution_link, exercise_id, submitter_id, comment_link_1, comment_link_2, comment_link_3)
            VALUES (:solution_link, :exercise_id, :submitter_id, :comment_link_1, :comment_link_2, :comment_link_3)
            ON CONFLICT (submitter_id, exercise_id) 
            DO UPDATE SET solution_link=EXCLUDED.solution_link, comment_link_1=EXCLUDED.comment_link_1, comment_link_2=EXCLUDED.comment_link_2, comment_link_3=EXCLUDED.comment_link_3
        """)
        db.session.execute(sql, {
            "exercise_id": exercise_id, 
            "submitter_id": submitter_id,
            "solution_link": solution_link,  
            "comment_link_1": comment_link_1, 
            "comment_link_2": comment_link_2, 
            "comment_link_3": comment_link_3
        })
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error adding or updating solution: {str(e)}")
    