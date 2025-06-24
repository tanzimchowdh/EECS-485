"""
Insta485 create view.

URLs include:
/accounts/create
"""

import uuid
import pathlib
import hashlib
from flask import (
    redirect,
    render_template,
    request,
    session,
    url_for,
    abort
)
import insta485


@insta485.app.route('/accounts/create/', methods=['GET', 'POST'])
def show_create():
    """Display /accounts/create/ route."""
    if session.get('user_id'):
        return redirect(url_for('show_edit'))
    if request.method == 'POST':
        file = request.files['file']
        username = request.form['username']
        password = request.form['password']
        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(file.filename).suffix
        )

        # Connect to database
        connection = insta485.model.get_db()

        # Query database
        cur = connection.execute(
            "SELECT username "
            "FROM users"
        )

        users = cur.fetchall()
        user_list = [u for u in users if u['username'] == username]
        if user_list:
            abort(409, description="Username already exists")
        if not password:
            abort(400, description="Password cannot be empty")

        algorithm = 'sha512'

        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_db_string = "$".join([algorithm, salt, hash_obj.hexdigest()])

        sql = """INSERT INTO users
                    (username, fullname, email, filename, password)
                    VALUES (?, ?, ?, ?, ?)"""
        val = (username, request.form['fullname'], request.form['email'],
               uuid_basename, password_db_string)
        connection.cursor().execute(sql, val)
        connection.commit()
        file.save(insta485.app.config["UPLOAD_FOLDER"]/uuid_basename)
        session['user_id'] = username
        return redirect(url_for('show_index'))

    return render_template("create.html")
