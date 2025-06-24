"""REST API for newest posts."""
import insta485


@insta485.app.route('/api/v1/p/', methods=["GET"])
def get_posts(size=10, page=1):
    """Return a list of posts."""
    if 'user_id' not in insta485.flask.session:
        cont_dict = {
            "message": "Forbidden",
            "status_code": 403
        }
        # Return error for posts API
        return insta485.flask.jsonify(**cont_dict), 403

    connection = insta485.model.get_db()
    size = insta485.flask.request.args.get("size", default=10, type=int)
    page = insta485.flask.request.args.get("page", default=0, type=int)
    if (size < 0 or page < 0):
        context = {
            "message": "Bad Request",
            "status_code": 400
        }
        return insta485.flask.jsonify(**context)

    sql = """SELECT postid
        FROM posts
        WHERE owner=?
        OR owner=(
            SELECT username2
            FROM following
            WHERE username1=?
        )
        ORDER BY postid DESC
        LIMIT ?
        OFFSET ?"""
    ins = connection.cursor()
    ins.execute(sql, (insta485.flask.session['user_id'],
                      insta485.flask.session['user_id'], size, page*size))
    posts = ins.fetchall()

    sql = """SELECT COUNT(postid)
        FROM posts
        WHERE owner=?
        OR owner=(
            SELECT username2
            FROM following
            WHERE username1=?
        )"""
    count_query = connection.execute(sql, (insta485.flask.session['user_id'],
                                           insta485.flask.session['user_id']))
    count = count_query.fetchone()['COUNT(postid)']

    for post in posts:
        post['url'] = "/api/v1/p/" + str(post['postid']) + "/"
    context = {
        "results": posts,
        "url": insta485.flask.request.path
    }
    if size*(page+1) >= count:
        context['next'] = ""
    else:
        context['next'] = "/api/v1/p/?size=" \
                          + str(size) + "&page=" + str(page + 1)
    return insta485.flask.jsonify(**context)
