from flask import render_template, request, redirect, url_for, session
from components import users, exercises, solutions, permissions


def register_routes(app):


    @app.route('/')
    def index_route():
        all_exercises = exercises.get_all_exercises()
        return render_template('index.html', exercises=all_exercises)


    @app.route('/request_permission', methods=['GET', 'POST'])
    def request_permission_route():
        error = None
        if request.method == 'POST':
            github_handle = request.form.get('github_handle')
            requested_role = request.form.get('requested_role')
            
            try:
                permissions.add_permission_request(github_handle, requested_role)
                return redirect(url_for('login_route'))
            except Exception as e:
                error = f"Error occurred: {str(e)}"

        csrf_token = users.get_or_create_csrf_token()
        return render_template('request_permission.html', error=error, csrf_token=csrf_token)


    @app.route('/manage_permissions', methods=['GET', 'POST'])
    def manage_permissions_route():
        error = None

        if request.method == 'POST':
            users.check_csrf()
            action = request.form.get('action')
            request_id = request.form.get('request_id')
            github_handle = request.form.get('github_handle')
            role = request.form.get('role')

            if action == 'approve':
                permissions.update_request_status(request_id, 'approved')
                permissions.add_permitted_user(github_handle, role)
            elif action == 'reject':
                permissions.update_request_status(request_id, 'rejected')
            else:
                try:
                    permissions.add_permitted_user(github_handle, role)
                except Exception as e:
                    error = f"Error occurred: {str(e)}"

        requests = permissions.get_pending_permission_requests()
        permitted_users = permissions.get_all_permitted_users()
        csrf_token = users.get_or_create_csrf_token()

        return render_template('manage_permissions.html', requests=requests, permitted_users=permitted_users, error=error, csrf_token=csrf_token)


    @app.route('/delete_permitted_user/<string:github_handle>', methods=['POST'])
    def delete_permitted_user_route(github_handle):
        try:
            permissions.delete_permitted_user(github_handle)
            return redirect(url_for('manage_permissions_route'))
        except Exception as e:
            error = f"Error occurred: {str(e)}"
            return render_template('manage_permissions.html', error=error)


    @app.route('/register', methods=['GET', 'POST'])
    def register_route():
        error = None
        if request.method == 'POST':
            github_handle = request.form.get('github_handle')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            
            if not github_handle or not password1 or not password2:
                error = "All fields are required"
            elif password1 != password2:
                error = "Passwords do not match"
            elif len(password1) < 4:
                error = "Password should be at least 4 characters long"

            if not error:
                try:
                    users.register_user(github_handle, password1)
                    users.login_user(github_handle, password1)
                    return redirect(url_for('index_route'))
                except Exception as e:
                    error = f"Error occurred: {str(e)}"

        csrf_token = users.get_or_create_csrf_token()
        return render_template('register.html', error=error, csrf_token=csrf_token)


    @app.route('/login', methods=['GET', 'POST'])
    def login_route():
        error = None
        if request.method == 'POST':
            github_handle = request.form.get('github_handle')
            password = request.form.get('password')

            if not github_handle or not password:
                error = "Both github handle and password are required"
            else:
                try:
                    if users.login_user(github_handle, password):
                        return redirect(url_for('index_route'))
                    else:
                        error = "Invalid credentials"
                except Exception as e:
                    error = f"Error occurred: {str(e)}"

        csrf_token = users.get_or_create_csrf_token()
        return render_template('login.html', error=error, csrf_token=csrf_token)


    @app.route('/logout')
    def logout_route():
        users.logout_user()
        return redirect(url_for('index_route'))


    @app.route('/exercise/<int:exercise_id>', methods=['GET'])
    def display_exercise_route(exercise_id):
        exercise = exercises.get_exercise_by_id(exercise_id)
        creator = exercises.get_creator_of_exercise(exercise_id)
        solution_data = None
        if "user_id" in session:
            solution_data = solutions.get_solution_by_user_and_exercise(session["user_id"], exercise_id)

        return render_template('exercise_display.html', exercise=exercise, creator=creator, solution_data=solution_data)


    @app.route('/create_exercise', methods=['GET', 'POST'])
    def create_exercise_route():
        error = None
        if request.method == 'POST':
            users.check_csrf()
            name = request.form.get('name')
            tasks = request.form.get('tasks')

            if not name or not tasks:
                error = "Both name and tasks are required"
            else:
                user = users.get_user_by_github_handle(session['github_handle'])

                if not user or user[3] != 'teacher':
                    return redirect(url_for('index_route'))

                creator_id = user[0]
                try:
                    exercises.create_exercise(name, tasks, creator_id)
                    return redirect(url_for('index_route'))
                except Exception as e:
                    error = f"Error occurred: {str(e)}"
                
        return render_template('exercise_create.html', error=error)


    @app.route('/exercise/<int:exercise_id>/edit', methods=['GET', 'POST'])
    def edit_exercise_route(exercise_id):
        error = None
        exercise = exercises.get_exercise_by_id(exercise_id)
        
        if not exercise:
            error = "Exercise not found"
            return render_template('index.html', error=error)
        
        creator = exercises.get_creator_of_exercise(exercise_id)
        if session.get('user_id') != creator.id:
            error = "Unauthorised access"
            return render_template('index.html', error=error)

        if request.method == 'POST':
            users.check_csrf()
            name = request.form.get('name')
            tasks = request.form.get('tasks')
            
            if not name or not tasks:
                error = "Both name and tasks are required"
            else:
                try:
                    exercises.update_exercise(exercise_id, name, tasks)
                    return redirect(url_for('display_exercise_route', exercise_id=exercise_id))
                except Exception as e:
                    error = f"Error occurred: {str(e)}"
        
        return render_template('exercise_edit.html', exercise=exercise, error=error)


    @app.route('/exercise/<int:exercise_id>/delete', methods=['POST'])
    def delete_exercise_route(exercise_id):
        error = None
        if request.method == 'POST':
            users.check_csrf()
            user = users.get_user_by_github_handle(session['github_handle'])

            if not user or user[3] != 'teacher':
                error = "Unauthorised access"

            try:
                exercises.delete_exercise(exercise_id, user[0])
                return redirect(url_for('index_route'))
            except Exception as e:
                error = f"Error occurred: {str(e)}"
            
        return render_template('index.html', error=error)


    @app.route('/exercise/<int:exercise_id>/submit_solution', methods=['POST'])
    def submit_solution_route(exercise_id):
        error = None
        if request.method == 'POST':
            users.check_csrf()
            solution_link = request.form.get('solution_link')
            comment_link_1 = request.form.get('comment_link_1')
            comment_link_2 = request.form.get('comment_link_2')
            comment_link_3 = request.form.get('comment_link_3')

            try:
                user = users.get_user_by_github_handle(session['github_handle'])
                submitter_id = user[0]
                solutions.submit_or_update_solution(exercise_id, submitter_id, solution_link, comment_link_1, comment_link_2, comment_link_3)
                return redirect(url_for('display_exercise_route', exercise_id=exercise_id))
            except Exception as e:
                error = f"Error occurred: {str(e)}"

        exercise = exercises.get_exercise_by_id(exercise_id)
        return render_template('exercise_display.html', exercise=exercise, error=error)
