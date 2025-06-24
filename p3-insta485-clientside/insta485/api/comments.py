"""REST api for post comments."""
import insta485


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/comments/',
                    methods=["GET", "POST"])
def get_comments(postid_url_slug):
    """Return the details for all comments on one post."""
    if 'user_id' not in insta485.flask.session:
        # Check for logged in user in comments API
        context_dict = {
            "message": "Forbidden",
            "status_code": 403
        }
        return insta485.flask.jsonify(**context_dict), 403

    # Connect to database
    connection = insta485.model.get_db()
    sql = "SELECT MIN(postid) FROM posts"
    minimum = connection.execute(sql).fetchone()['MIN(postid)']
    sql = "SELECT MAX(postid) FROM posts"
    maximum = connection.execute(sql).fetchone()['MAX(postid)']
    if postid_url_slug > maximum or postid_url_slug < minimum:
        context = {
            "message": "Not Found",
            "status_code": 404
        }
        return insta485.flask.jsonify(**context), 404

    if insta485.flask.request.method == "POST":
        data = insta485.flask.request.get_json()
        vals = (insta485.flask.session['user_id'],
                postid_url_slug, data['text'])
        connection.cursor().execute("""INSERT INTO comments
                                        (owner, postid, text)
                                        VALUES (?, ?, ?)""", vals)
        connection.commit()
        sql = """SELECT commentid, owner, postid,
              text FROM comments ORDER BY commentid DESC LIMIT 1"""
        comment_request = connection.execute(sql)
        context = comment_request.fetchone()
        context['owner_show_url'] = "/u/" + context['owner'] + "/"
        return insta485.flask.jsonify(**context), 201

    sql = "SELECT commentid, owner, postid, text FROM comments WHERE postid=?"
    ins = connection.cursor()
    ins.execute(sql, (postid_url_slug,))
    comments = ins.fetchall()

    for comment in comments:
        comment['owner_show_url'] = "/u/" + comment['owner'] + "/"

    context = {
        "comments": comments,
        "url": insta485.flask.request.path
    }
    return insta485.flask.jsonify(**context)
