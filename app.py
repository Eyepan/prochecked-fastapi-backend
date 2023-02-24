from flask import Flask, jsonify, request
import mysql.connector
from uuid import uuid4

app = Flask(__name__)

config = {
    "user": "panpanpan",
    "password": "mynameisiyappan",
    "host": "panpanpan.mysql.pythonanywhere-services.com",
    "database": "panpanpan$prochecked",
    "port": 3306,
    "raise_on_warnings": False
}

if __name__ == "__main__":
    config = {
        "user": "root",
        "password": "",
        "host": "localhost",
        "database": "prochecked",
        "port": 3306,
        "raise_on_warnings": False
    }

app.app_context().push()
mysql = mysql.connector.connect(**config)

cursor = mysql.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(36) PRIMARY KEY,
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        type VARCHAR(20) DEFAULT 'Team Member'
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS projects (
        id VARCHAR(36) PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        team_leader_id VARCHAR(36),
        FOREIGN KEY (team_leader_id) REFERENCES users(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id VARCHAR(36) PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        project_id VARCHAR(36),
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
        created DATE NOT NULL,
        deadline DATE NOT NULL
    );
    """
)
mysql.commit()
cursor.close()


@app.route('/api/users')
def list_users():
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    desc = cursor.description
    cursor.close()
    if not users:
        return {"error": "no users found"}, 404
    return jsonify([dict(zip([key[0] for key in desc], user)) for user in users])


@app.route('/api/users', methods=['POST'])
def add_user():
    cursor = mysql.cursor()
    if not request.json or not 'email' in request.json or not 'password' in request.json:
        return {"error": "missing fields"}, 400
    email = request.json['email']
    password = request.json['password']
    userType = request.json.get('type', 'Team Member')
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if user:
        return {"error": "user with the given email already exists"}, 409
    cursor.execute(
        "INSERT INTO users (id, email, password, type) VALUES (%s, %s, %s, %s)", (str(uuid4()), email, password, userType))
    mysql.commit()
    cursor.close()
    return {"message": "user successfully added"}, 200


@app.route('/api/users/<id>', methods=['GET'])
def get_user(id):
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "user not found"}, 404
    desc = cursor.description
    cursor.close()
    return dict(zip([key[0] for key in desc], user))


@app.route("/api/users/signin", methods=['POST'])
def sign_in():
    cursor = mysql.cursor()
    if not request.json or not 'email' in request.json or not 'password' in request.json:
        return {"error": "missing fields"}, 400
    email = request.json['email']
    password = request.json['password']
    cursor.execute(
        "SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()
    if not user:
        return {"error": "user not found"}, 404
    desc = cursor.description
    cursor.close()
    return dict(zip([key[0] for key in desc], user))


@app.route('/api/users/<id>', methods=['PUT'])
def update_user(id):
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "user not found"}, 404
    if not request.json or not 'email' in request.json or not 'password' in request.json:
        return {"error": "missing fields"}, 400
    email = request.json['email']
    password = request.json['password']
    userType = request.json.get('type', 'Team Member')
    cursor.execute(
        "UPDATE users SET email = %s, password = %s, type = %s WHERE id = %s",
        (email, password, userType, id))
    mysql.commit()
    cursor.close()
    return {"message": "user successfully updated"}, 200


@app.route('/api/users/<id>', methods=['DELETE'])
def delete_user(id):
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "user not found"}, 404
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    mysql.commit()
    cursor.close()
    return {"message": "user successfully deleted"}, 200


@app.route('/api/users/<user_id>/projects', methods=['POST'])
def create_project(user_id):
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "user not found"}, 404
    if not request.json or not 'title' in request.json:
        return {"error": "missing fields"}, 400
    title = request.json['title']
    description = request.json.get('description', '')
    cursor.execute(
        "INSERT INTO projects (id, title, description, team_leader_id) VALUES (%s, %s, %s, %s)",
        (str(uuid4()), title, description, user_id))
    mysql.commit()
    cursor.close()
    return {"message": "project successfully created"}, 200


@app.route('/api/users/<user_id>/projects')
def get_all_projects_for_user(user_id):
    cursor = mysql.cursor()
    cursor.execute(
        "SELECT * FROM projects WHERE team_leader_id = %s", (user_id,))
    projects = cursor.fetchall()
    desc = cursor.description
    cursor.close()
    if not projects:
        return {"error": "no projects found"}, 404
    return jsonify([dict(zip([key[0] for key in desc], project)) for project in projects])


@app.route('/api/users/<user_id>/projects/<project_id>', methods=['GET'])
def get_project(user_id, project_id):
    cursor = mysql.cursor()
    cursor.execute(
        "SELECT * FROM projects WHERE id = %s AND team_leader_id = %s", (project_id, user_id))
    project = cursor.fetchone()
    if not project:
        return {"error": "project not found"}, 404
    desc = cursor.description
    cursor.close()
    return dict(zip([key[0] for key in desc], project))


@app.route('/api/users/<user_id>/projects/<project_id>', methods=['PUT'])
def update_project(user_id, project_id):
    cursor = mysql.cursor()
    cursor.execute(
        "SELECT * FROM projects WHERE id = %s AND team_leader_id = %s", (project_id, user_id))
    project = cursor.fetchone()
    if not project:
        return {"error": "project not found"}, 404
    if not request.json or not 'title' in request.json:
        return {"error": "missing fields"}, 400
    title = request.json['title']
    description = request.json.get('description', '')
    cursor.execute(
        "UPDATE projects SET title = %s, description = %s WHERE id = %s",
        (title, description, project_id))
    mysql.commit()
    cursor.close()
    return {"message": "project successfully updated"}, 200


@app.route('/api/users/<user_id>/projects/<project_id>', methods=['DELETE'])
def delete_project(user_id, project_id):
    cursor = mysql.cursor()
    cursor.execute(
        "SELECT * FROM projects WHERE id = %s AND team_leader_id = %s", (project_id, user_id))
    project = cursor.fetchone()
    if not project:
        return {"error": "project not found"}, 404
    cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
    mysql.commit()
    cursor.close()
    return {"message": "project successfully deleted"}, 200


@app.route('/api/users/<user_id>/projects/<project_id>/tasks', methods=['POST'])
def create_task(user_id, project_id):
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "user not found"}, 404
    cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cursor.fetchone()
    if not project:
        return {"error": "project not found"}, 404
    if not request.json or not 'title' in request.json or not 'description' in request.json or not 'created' in request.json or not 'deadline' in request.json:
        return {"error": "missing fields"}, 400
    title = request.json['title']
    description = request.json['description']
    created = request.json['created']
    deadline = request.json['deadline']
    cursor.execute(
        "INSERT INTO tasks (id, title, description, project_id, created, deadline) VALUES (%s, %s, %s, %s, %s, %s)", (str(uuid4()), title, description, project_id, created, deadline))
    mysql.commit()
    cursor.close()
    return {"message": "task successfully added"}, 200


@app.route('/api/users/<user_id>/projects/<project_id>/tasks/<task_id>', methods=['GET'])
def get_task(user_id, project_id, task_id):
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "user not found"}, 404
    cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cursor.fetchone()
    if not project:
        return {"error": "project not found"}, 404
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    if not task:
        return {"error": "task not found"}, 404
    desc = cursor.description
    cursor.close()
    return dict(zip([key[0] for key in desc], task))


@app.route('/api/users/<user_id>/projects/<project_id>/tasks', methods=['GET'])
def get_all_tasks_for_project(user_id, project_id):
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "user not found"}, 404
    cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cursor.fetchone()
    if not project:
        return {"error": "project not found"}, 404
    cursor.execute("SELECT * FROM tasks WHERE project_id = %s", (project_id,))
    tasks = cursor.fetchall()
    desc = cursor.description
    cursor.close()
    if not tasks:
        return {"error": "no tasks found"}, 404
    return jsonify([dict(zip([key[0] for key in desc], task)) for task in tasks])


@app.route('/api/users/<user_id>/projects/<project_id>/tasks/<task_id>', methods=['PUT'])
def update_task(user_id, project_id, task_id):
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "user not found"}, 404

    # Check if project exists
    cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cursor.fetchone()
    if not project:
        return {"error": "project not found"}, 404
    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    if not task:
        return {"error": "task not found"}, 404
    # Check if task belongs to project
    if task[3] != project_id:
        return {"error": "task does not belong to project"}, 404
    # Check if user is team leader of project or assigned to task
    cursor.execute("SELECT * FROM users WHERE id = %s", (project[3],))
    team_leader = cursor.fetchone()
    if user_id != project[3] and user_id != task[4]:
        return {"error": "user not authorized to modify task"}, 401
    # Update task
    title = request.json.get('title', task[1])
    description = request.json.get('description', task[2])
    created = request.json.get('created', task[5])
    deadline = request.json.get('deadline', task[6])
    cursor.execute("UPDATE tasks SET title = %s, description = %s, created = %s, deadline = %s WHERE id = %s",
                   (title, description, created, deadline, task_id))
    mysql.commit()
    cursor.close()
    return {"message": "task successfully updated"}, 200


@app.route('/api/users/<user_id>/projects/<project_id>/tasks/<task_id>', methods=['DELETE'])
def delete_task(user_id, project_id, task_id):
    cursor = mysql.cursor()
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "user not found"}, 404
    # Check if project exists
    cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cursor.fetchone()
    if not project:
        return {"error": "project not found"}, 404
    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    if not task:
        return {"error": "task not found"}, 404
    # Check if task belongs to project
    if task[3] != project_id:
        return {"error": "task does not belong to project"}, 404
    # Check if user is team leader of project or assigned to task
    cursor.execute("SELECT * FROM users WHERE id = %s", (project[3],))
    team_leader = cursor.fetchone()
    if user_id != project[3] and user_id != task[4]:
        return {"error": "user not authorized to delete task"}, 401
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    mysql.commit()
    cursor.close()
    return {"message": "task successfully deleted"}, 200


if __name__ == '__main__':
    app.run(debug=True)
