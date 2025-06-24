"""
Insta485 login view.

URLs include:
/accounts/login
"""
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


@insta485.app.route('/accounts/login/', methods=['GET', 'POST'])
def show_login():
    """Display /accounts/login/ route."""
    if 'user_id' in session:
        return redirect(url_for('show_index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        algorithm = 'sha512'
        hash_obj = hashlib.new(algorithm)

        # Connect to database
        connection = insta485.model.get_db()

        # Query database
        cur = connection.execute(
            "SELECT username, password "
            "FROM users"
        )

        users = cur.fetchall()
        user_list = [u for u in users if u['username'] == username]
        if not user_list:
            abort(403, description="Invalid login")
        user = user_list[0]
        salt = user['password'].split('$')[1]
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])
        if user and user['password'] == password_db_string:
            session['user_id'] = user['username']
            return redirect(url_for('show_index'))
        abort(403, description="Invalid login")

    return render_template("login.html")
