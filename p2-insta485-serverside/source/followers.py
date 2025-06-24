"""
Insta485 follower view.

URLs include:
/u/user_url_slug/follower
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


@insta485.app.route('/u/<path:user_url_slug>/followers/',
                    methods=['GET', 'POST'])
def show_followers(user_url_slug):
    """Display /u/<path:user_url_slug>/followers/ route."""
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

    sql = "SELECT username1 FROM following WHERE username2 = ?"
    ins = connection.cursor()
    ins.execute(sql, (user_url_slug,))
    user_followers = ins.fetchall()

    sql = "SELECT username2 FROM following WHERE username1 = ?"
    ins = connection.cursor()
    ins.execute(sql, (session['user_id'],))
    logname_following = ins.fetchall()

    cur_users = connection.execute(
        "SELECT username, filename "
        "FROM users"
    )
    all_users = cur_users.fetchall()

    followers = list()
    for fol in user_followers:
        fol_dict = {}
        fol_dict['username'] = fol['username1']
        fol_dict['logname_follows_username'] = False
        for log in logname_following:
            if fol['username1'] == log['username2']:
                fol_dict['logname_follows_username'] = True
        for user in all_users:
            if fol['username1'] == user['username']:
                fol_dict['user_img_url'] = user['filename']
        followers.append(fol_dict)
    context = {"logname": session['user_id'],
               "username": user_url_slug, "followers": followers}
    return render_template("followers.html", **context)
