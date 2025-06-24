"""
Insta485 edit view.

URLs include:
/accounts/edit
"""
import uuid
import pathlib
import os
from flask import (
    redirect,
    render_template,
    request,
    session,
    url_for
)
import insta485


@insta485.app.route('/accounts/edit/', methods=['GET', 'POST'])
def show_edit():
    """Display /accounts/edit/ route."""
    if 'user_id' not in session:
        return redirect(url_for('show_login'))

    # connect to the database
    connection = insta485.model.get_db()

    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        if filename != '':
            uuid_basename = "{stem}{suffix}".format(
                stem=uuid.uuid4().hex,
                suffix=pathlib.Path(filename).suffix
            )
            sql = "SELECT filename FROM users WHERE username=?"
            cur_file = connection.cursor()
            cur_file.execute(sql, (session['user_id'],))
            old_file = cur_file.fetchall()[0]['filename']
            os.remove(insta485.app.config['UPLOAD_FOLDER']/old_file)
            file.save(insta485.app.config['UPLOAD_FOLDER']/uuid_basename)
            sql = "UPDATE users SET filename=? WHERE username=?"
            vals = (uuid_basename, session['user_id'])
            cur_file.execute(sql, vals)
            connection.commit()

        fullname = request.form['fullname']
        email = request.form['email']
        # Query database
        sql = "UPDATE users SET fullname=?, email=? WHERE username=?"
        vals = (fullname, email, session['user_id'])
        ins = connection.cursor()
        ins.execute(sql, vals)
        connection.commit()

    # query database
    sql = ("SELECT fullname, email, filename FROM users WHERE username=?")
    ins = connection.cursor()
    ins.execute(sql, (session['user_id'],))
    user = ins.fetchall()
    context = {"logname": session['user_id'], "fullname": user[0]['fullname'],
               "email": user[0]['email'], "img_url": user[0]['filename']}

    return render_template("edit.html", **context)
