"""
Insta485 index (main) view.

URLs include:
/
"""
import os
import pathlib
import uuid
import hashlib
import arrow
from flask import (
    redirect,
    render_template,
    request,
    session,
    send_from_directory,
    url_for,
    abort
)
import insta485


@insta485.app.route('/', methods=['GET', 'POST'])
def show_index():
    """Display / route."""
    if 'user_id' not in session:
        return redirect(url_for('show_login'))

    # Connect to database
    connection = insta485.model.get_db()

    if request.method == 'POST':
        if 'like' in request.form:
            connection.cursor().execute("""INSERT INTO likes
                                        (owner, postid) VALUES (?, ?)""",
                                        (session['user_id'],
                                         request.form['postid']))
            connection.commit()
        elif 'unlike' in request.form:
            connection.cursor().execute("""DELETE FROM likes
                                        WHERE owner=? AND postid=?""",
                                        (session['user_id'],
                                         request.form['postid']))
            connection.commit()
        elif 'comment' in request.form:
            cur_count = connection.execute(
                "SELECT MAX(commentid) "
                "FROM comments"
            )
            cid = cur_count.fetchone()
            commentid = cid['MAX(commentid)'] + 1
            connection.cursor().execute("""INSERT INTO comments
                                        (commentid, owner, postid, text)
                                        VALUES (?, ?, ?, ?)""",
                                        (commentid, session['user_id'],
                                         request.form['postid'],
                                         request.form['text']))
            connection.commit()

    all_following = connection.execute(
        "SELECT * "
        "FROM following"
    ).fetchall()
    all_posts = connection.execute(
        "SELECT * "
        "FROM posts"
    ).fetchall()
    all_likes = connection.execute(
        "SELECT * "
        "FROM likes"
    ).fetchall()
    comms = connection.execute(
        "SELECT * "
        "FROM comments"
    ).fetchall()
    all_users = connection.execute(
        "SELECT username, filename "
        "FROM users"
    ).fetchall()

    posts = list()
    following_list = [f for f in all_following
                      if f['username1'] == session['user_id']]
    for post in all_posts:
        if post['owner'] == session['user_id']:
            posts.append(post)
        for fol in following_list:
            if post['owner'] == fol['username2']:
                posts.append(post)

    for post in posts:
        post['created'] = arrow.get(post['created']).humanize()
        likes = [like for like in all_likes
                 if like['postid'] == post['postid']]
        post['likes'] = len(likes)
        if [k for k in likes if k['owner'] == session['user_id']]:
            post['logname_likes_post'] = True
        post['comments'] = [c for c in comms if c['postid'] == post['postid']]
        users = [u for u in all_users if u['username'] == post['owner']]
        post['owner_img_url'] = users[0]['filename']

    return render_template("index.html",
                           **{"logname": session['user_id'], "posts": posts})
