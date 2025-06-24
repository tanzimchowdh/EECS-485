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
            ).fetchone()
            commentid = cur_count['MAX(commentid)'] + 1
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

    posts.reverse()
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
            connection.cursor().execute(sql, (session['user_id'],
                                              request.form['username']))
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
            post_fetch = connection.execute(
                "SELECT MAX(postid) "
                "FROM posts"
            ).fetchone()
            post_count = 1
            if isinstance(post_fetch['MAX(postid)'], int):
                post_count = post_fetch['MAX(postid)'] + 1
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


@insta485.app.route('/accounts/logout/', methods=['POST'])
def show_logout():
    """Display logout route."""
    session.clear()
    return redirect(url_for('show_login'))


@insta485.app.route('/accounts/create/', methods=['GET', 'POST'])
def show_create():
    """Display /accounts/create/ route."""
    if session.get('user_id'):
        return redirect(url_for('show_edit'))
    if request.method == 'POST':
        file = request.files['file']
        username = request.form['username']
        password = request.form['password']
        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(file.filename).suffix
        )

        # Connect to database
        connection = insta485.model.get_db()

        # Query database
        cur = connection.execute(
            "SELECT username "
            "FROM users"
        )

        users = cur.fetchall()
        user_list = [u for u in users if u['username'] == username]
        if user_list:
            abort(409, description="Username already exists")
        if not password:
            abort(400, description="Password cannot be empty")

        algorithm = 'sha512'

        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_db_string = "$".join([algorithm, salt, hash_obj.hexdigest()])

        sql = """INSERT INTO users
                    (username, fullname, email, filename, password)
                    VALUES (?, ?, ?, ?, ?)"""
        val = (username, request.form['fullname'], request.form['email'],
               uuid_basename, password_db_string)
        connection.cursor().execute(sql, val)
        connection.commit()
        file.save(insta485.app.config["UPLOAD_FOLDER"]/uuid_basename)
        session['user_id'] = username
        return redirect(url_for('show_index'))

    return render_template("create.html")


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


@insta485.app.route('/uploads/<path:filename>', methods=['GET'])
def show_image(filename):
    """Display /uploads/<path::filename> route."""
    if 'user_id' not in session:
        abort(403, description="Must be logged in")
    return send_from_directory(insta485.app.config['UPLOAD_FOLDER'], filename)


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
