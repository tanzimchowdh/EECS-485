"""
Insta485 delete view.

URLs include:
/accounts/delete
"""
import os
from flask import (
    redirect,
    render_template,
    request,
    session,
    url_for
)
import insta485


@insta485.app.route('/accounts/delete/', methods=['GET', 'POST'])
def show_delete():
    """Display delete account route."""
    if 'user_id' not in session:
        return redirect(url_for('show_login'))

    # connect to the database
    connection = insta485.model.get_db()
    files = list()

    if request.method == 'POST':
        cur = connection.cursor()
        sql = "SELECT filename FROM users WHERE username=?"
        cur.execute(sql, (session['user_id'],))
        filename = cur.fetchall()[0]['filename']
        files.append(filename)
        sql = "SELECT filename FROM posts WHERE owner=?"
        cur.execute(sql, (session['user_id'],))
        post_files = cur.fetchall()
        for p_file in post_files:
            files.append(p_file['filename'])
        sql = "DELETE FROM users WHERE username=?"
        cur.execute(sql, (session['user_id'],))
        for f_image in files:
            os.remove(insta485.app.config['UPLOAD_FOLDER']/f_image)
        session.clear()
        return redirect(url_for('show_create'))

    context = {"logname": session['user_id']}
    return render_template("delete.html", **context)
