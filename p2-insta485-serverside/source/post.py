"""
Insta485 post view.

URLs include:
/p/postid_url_slug
"""

import os
from flask import (
    redirect,
    render_template,
    request,
    session,
    url_for,
    abort
)
import arrow
import insta485


@insta485.app.route('/p/<path:postid_url_slug>/', methods=['GET', 'POST'])
def show_post(postid_url_slug):
    """Display /p/<path:postid_url_slug>/ route."""
    if 'user_id' not in session:
        return redirect(url_for('show_login'))

    # Connect to database
    connection = insta485.model.get_db()

    if request.method == 'POST':
        if "like" in request.form:
            vals = (session['user_id'], request.form['postid'])
            connection.cursor().execute("""INSERT INTO likes (owner, postid)
                                        VALUES (?, ?)""", vals)
            connection.commit()
        elif "unlike" in request.form:
            vals = (session['user_id'], request.form['postid'])
            connection.cursor().execute("""DELETE FROM likes
                                        WHERE owner=? AND postid=?""", vals)
            connection.commit()
        elif "comment" in request.form:
            cur_count = connection.execute(
                "SELECT MAX(commentid) "
                "FROM comments"
            )
            cid = cur_count.fetchone()
            commentid = cid['MAX(commentid)'] + 1
            vals = (commentid, session['user_id'],
                    request.form['postid'], request.form['text'])
            connection.cursor().execute("""INSERT INTO comments
                                        (commentid, owner, postid, text)
                                        VALUES (?, ?, ?, ?)""", vals)
            connection.commit()
        elif "uncomment" in request.form:
            ins = connection.cursor().execute("""SELECT owner FROM comments
                                              WHERE commentid=?""",
                                              (request.form['commentid'],))
            comment_owner = ins.fetchall()[0]['owner']
            if session['user_id'] != comment_owner:
                abort(403, description="Forbidden delete comment request")
            connection.cursor().execute("""DELETE FROM comments
                                        WHERE commentid=?""",
                                        (request.form['commentid'],))
            connection.commit()
        elif "delete" in request.form:
            old_pst = connection.cursor().execute("""SELECT filename, owner
                                                  FROM posts
                                                  WHERE postid=?""",
                                                  (postid_url_slug,
                                                   )).fetchall()[0]
            post_owner = old_pst['owner']
            if session['user_id'] != post_owner:
                abort(403, description="Forbidden delete post request")
            connection.cursor().execute("""DELETE FROM posts
                                        WHERE postid=?""", (postid_url_slug,))
            connection.commit()
            os.remove(insta485.app.config["UPLOAD_FOLDER"]/old_pst['filename'])
            return redirect(url_for('show_user',
                            user_url_slug=session['user_id']))

    sql = "SELECT * FROM posts WHERE postid=?"
    post = connection.cursor().execute(sql, (postid_url_slug,)).fetchall()[0]
    context = {"logname": session['user_id'], "postid": postid_url_slug,
               "owner": post['owner'], "img_url": post['filename'],
               "timestamp": arrow.get(post['created']).humanize()}

    sql = "SELECT filename FROM users WHERE username=?"
    ins = connection.cursor().execute(sql, (post['owner'],))
    context['owner_img_url'] = ins.fetchall()[0]['filename']

    sql = "SELECT owner FROM likes WHERE postid=?"
    like_dict = connection.cursor().execute(sql,
                                            (postid_url_slug,)).fetchall()
    context['likes'] = len(like_dict)
    context['logname_likes_post'] = False
    if {"owner": session['user_id']} in like_dict:
        context['logname_likes_post'] = True

    sql = "SELECT commentid, owner, text FROM comments WHERE postid=?"
    context['comments'] = connection.cursor().execute(sql, (postid_url_slug,
                                                            )).fetchall()
    return render_template("post.html", **context)
