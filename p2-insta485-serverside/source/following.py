"""
Insta485 following view.

URLs include:
/u/<user_url_slug>/following
"""
from flask import (
    redirect,
    render_template,
    request,
    session,
    url_for,
    abort
)
import insta485


@insta485.app.route('/u/<path:user_url_slug>/following/',
                    methods=['GET', 'POST'])
def show_following(user_url_slug):
    """Display /u/<user_url_slug>/following route."""
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    # Connect to database
    connection = insta485.model.get_db()

    if request.method == 'POST':
        if 'follow' in request.form:
            sql = "INSERT INTO following (username1, username2) VALUES (?, ?)"
            vals = (session['user_id'], request.form['username'])
            ins = connection.cursor()
            ins.execute(sql, vals)
            connection.commit()
        elif 'unfollow' in request.form:
            sql = "DELETE FROM following WHERE username1=? AND username2=?"
            vals = (session['user_id'], request.form['username'])
            ins = connection.cursor()
            ins.execute(sql, vals)
            connection.commit()

    sql = "SELECT username FROM users WHERE username=?"
    ins = connection.cursor()
    ins.execute(sql, (user_url_slug,))
    if len(ins.fetchall()) == 0:
        abort(404, description="User doesn't exist")

    sql = "SELECT username2 FROM following WHERE username1=?"
    ins = connection.cursor()
    ins.execute(sql, (session['user_id'],))
    log_following = ins.fetchall()

    ins.execute(sql, (user_url_slug,))
    user_following = ins.fetchall()

    cur_users = connection.execute(
        "SELECT username, filename "
        "FROM users"
    )
    users = cur_users.fetchall()

    following = list()
    for follow in user_following:
        fol_dict = {}
        fol_dict['username'] = follow['username2']
        fol_dict['logname_follows_username'] = False
        for log in log_following:
            if follow['username2'] == log['username2']:
                fol_dict['logname_follows_username'] = True
        for user in users:
            if follow['username2'] == user['username']:
                fol_dict['user_img_url'] = user['filename']
        following.append(fol_dict)

    context = {"logname": session['user_id'],
               "username": user_url_slug, "following": following}
    return render_template("following.html", **context)
