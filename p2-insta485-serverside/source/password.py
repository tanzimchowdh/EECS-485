"""
Insta485 post view.

URLs include:
/p/postid_url_slug
"""
import uuid
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


@insta485.app.route('/accounts/password/', methods=['GET', 'POST'])
def show_password():
    """Display /accounts/password/ route."""
    if 'user_id' not in session:
        return redirect(url_for('show_login'))

    if request.method == 'POST':
        # Connect to database
        connection = insta485.model.get_db()
        sql = "SELECT password FROM users WHERE username=?"
        ins = connection.cursor()
        ins.execute(sql, (session['user_id'],))
        old_password_db_string = ins.fetchall()[0]['password']

        algorithm = 'sha512'
        hash_obj = hashlib.new(algorithm)
        salt = old_password_db_string.split('$')[1]
        password_input_salted = salt + request.form['password']
        hash_obj.update(password_input_salted.encode('utf-8'))
        password_input_db_string = "$".join([algorithm,
                                            salt, hash_obj.hexdigest()])

        if password_input_db_string != old_password_db_string:
            abort(403, description="Invalid password")
        new_password = request.form['new_password1']
        if new_password != request.form['new_password2']:
            abort(401, description="New passwords don't match")

        hash_obj = hashlib.new(algorithm)
        salt = uuid.uuid4().hex
        new_password_salted = salt + new_password
        hash_obj.update(new_password_salted.encode('utf-8'))
        new_password_hash = hash_obj.hexdigest()
        new_password_db_string = "$".join([algorithm, salt, new_password_hash])

        sql = "UPDATE users SET password=? WHERE username=?"
        val = (new_password_db_string, session['user_id'])
        ins = connection.cursor()
        ins.execute(sql, val)
        connection.commit()
        return redirect(url_for('show_edit'))

    context = {"logname": session['user_id']}
    return render_template("password.html", **context)
