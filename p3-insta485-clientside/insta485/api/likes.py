"""REST API for likes."""
import insta485


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/',
                    methods=["GET", "POST", "DELETE"])
def get_likes(postid_url_slug):
    """Return likes on postid."""
    if 'user_id' not in insta485.flask.session:
        # Check likes API for user
        context = {
            "message": "Forbidden",
            "status_code": 403
        }
        # For likes API return error dict
        return insta485.flask.jsonify(**context), 403

    query = "SELECT MIN(postid) FROM posts"
    connection = insta485.model.get_db()
    least = connection.execute(query).fetchone()['MIN(postid)']
    query = "SELECT MAX(postid) FROM posts"
    most = connection.execute(query).fetchone()['MAX(postid)']
    if postid_url_slug > most or postid_url_slug < least:
        context_dict = {
            "message": "Not Found",
            "status_code": 404
        }
        return insta485.flask.jsonify(**context_dict), 404

    if insta485.flask.request.method == "DELETE":
        sql = "SELECT * FROM likes WHERE owner=? AND postid=?"
        vals = (insta485.flask.session['user_id'], postid_url_slug)
        exists = len(connection.cursor().execute(sql, vals).fetchall())
        if exists:
            sql = "DELETE FROM likes WHERE owner=? AND postid=?"
            connection.cursor().execute(sql, vals)
            connection.commit()
        return '', 204
    if insta485.flask.request.method == "POST":
        sql = "SELECT owner FROM likes WHERE postid=? AND owner=?"
        session_id = insta485.flask.session['user_id']
        like = connection.cursor().execute(sql,
                                           (postid_url_slug,
                                            session_id)).fetchall()
        if len(like) != 0:
            context = {
                "logname": insta485.flask.session['user_id'],
                "message": "Conflict",
                "postid": postid_url_slug,
                "status_code": 409
            }
            return insta485.flask.jsonify(**context), 409

        vals = (insta485.flask.session['user_id'], postid_url_slug)
        connection.cursor().execute("""INSERT INTO likes (owner, postid)
                                    VALUES (?, ?)""", vals)
        connection.commit()
        sql = "SELECT owner, postid FROM likes WHERE owner=? AND postid=?"
        vals = (insta485.flask.session['user_id'], postid_url_slug)
        ins = connection.cursor()
        ins.execute(sql, vals)
        new_like = ins.fetchall()
        context = {
            "logname": new_like[0]['owner'],
            "postid": new_like[0]['postid']
        }
        return insta485.flask.jsonify(**context), 201

    sql = "SELECT owner FROM likes WHERE postid=?"
    likes_on_post = connection.cursor().execute(sql,
                                                (postid_url_slug,)).fetchall()
    context = {
        "logname_likes_this": 0,
        "likes_count": len(likes_on_post),
        "postid": postid_url_slug,
        "url": insta485.flask.request.path
        }
    if {"owner": insta485.flask.session['user_id']} in likes_on_post:
        context['logname_likes_this'] = 1

    return insta485.flask.jsonify(**context)
