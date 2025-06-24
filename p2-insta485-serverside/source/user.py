"""
Insta485 user view.

URLs include:
/u/user_url_slug
"""

import uuid
import pathlib
from flask import (
    redirect,
    render_template,
    request,
    session,
    url_for,
    abort
)
import insta485


@insta485.app.route('/u/<path:user_url_slug>/', methods=['GET', 'POST'])
def show_user(user_url_slug):
    """Display /u/<path::user_url_slug>/."""
    if 'user_id' not in session:
        return redirect(url_for('show_login'))

    # Connect to database
    connection = insta485.model.get_db()

    if request.method == 'POST':
        if 'follow' in request.form:
            sql = "INSERT INTO following (username1, username2) VALUES (?, ?)"
            vals = (session['user_id'], request.form['username'])
            connection.cursor().execute(sql, vals)
            connection.commit()
        elif 'unfollow' in request.form:
            sql = "DELETE FROM following WHERE username1=? AND username2=?"
            vals = (session['user_id'], request.form['username'])
            connection.cursor().execute(sql, vals)
            connection.commit()
        elif 'create_post' in request.form:
            file = request.files['file']
            uuid_basename = "{stem}{suffix}".format(
                stem=uuid.uuid4().hex,
                suffix=pathlib.Path(file.filename).suffix
            )
            cur = connection.execute(
                "SELECT MAX(postid) "
                "FROM posts"
            )
            post_count = cur.fetchone()['MAX(postid)'] + 1
            sql = """INSERT INTO posts (postid, filename, owner)
                VALUES (?, ?, ?)"""
            val = (post_count, uuid_basename, session['user_id'])
            connection.cursor().execute(sql, val)
            connection.commit()
            file.save(insta485.app.config["UPLOAD_FOLDER"]/uuid_basename)

    sql = "SELECT username, fullname FROM users WHERE username = ?"
    user = connection.cursor().execute(sql, (user_url_slug,)).fetchall()
    if len(user) == 0:
        abort(404, description="User doesn't exist")

    sql = "SELECT username2 FROM following WHERE username1 = ?"
    l_fol = connection.cursor().execute(sql, (session['user_id'],)).fetchall()

    sql = "SELECT COUNT(username1) FROM following WHERE username2=?"
    followers_count = connection.cursor().execute(sql, (user_url_slug,))

    sql = "SELECT COUNT(username2) FROM following WHERE username1=?"
    following_count = connection.cursor().execute(sql, (user_url_slug,))

    sql = "SELECT postid, filename FROM posts WHERE owner=?"
    ins = connection.cursor()
    ins.execute(sql, (user_url_slug,))

    context = {"logname": session['user_id'], "username": user[0]['username'],
               "fullname": user[0]['fullname']}
    if {'username2': user_url_slug} in l_fol:
        context['logname_follows_username'] = True
    else:
        context['logname_follows_username'] = False
    context['followers'] = followers_count.fetchone()['COUNT(username1)']
    context['following'] = following_count.fetchone()['COUNT(username2)']
    context['posts'] = ins.fetchall()
    context['total_posts'] = len(context['posts'])
    return render_template("user.html", **context)
