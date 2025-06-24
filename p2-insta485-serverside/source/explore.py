"""
Insta485 explore view.

URLs include:
/explore
"""
from flask import (
    redirect,
    render_template,
    request,
    session,
    url_for
)
import insta485


@insta485.app.route('/explore/', methods=['GET', 'POST'])
def show_explore():
    """Display /explore route."""
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

    sql = "SELECT username2 FROM following WHERE username1=?"

    ins = connection.cursor()
    ins.execute(sql, (session['user_id'],))
    all_following = ins.fetchall()

    ins = connection.cursor()
    ins.execute(
        "SELECT username, filename "
        "FROM users"
    )

    all_users = ins.fetchall()
    for user in all_users:
        if user['username'] == session['user_id']:
            all_users.remove(user)
            break
    for following in all_following:
        for users in all_users:
            if users['username'] == following['username2']:
                all_users.remove(users)
                break

    print(all_users)
    context = {'logname': session['user_id'], 'not_following': all_users}
    return render_template('explore.html', **context)
