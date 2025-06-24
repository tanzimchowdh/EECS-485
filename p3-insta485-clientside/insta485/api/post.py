"""REST API for 1 post."""
from flask import (
    request,
    session,
    jsonify
)
import insta485


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/', methods=["GET"])
def get_post(postid_url_slug):
    """Return the details for one post."""
    if 'user_id' not in session:
        # Check post API for logged in user
        con_dict = {
            "message": "Forbidden",
            "status_code": 403
        }
        # Return error dict for post API
        return jsonify(**con_dict), 403

    # Connect to database
    sql = "SELECT MIN(postid) FROM posts"
    connection = insta485.model.get_db()
    smallest = connection.execute(sql).fetchone()['MIN(postid)']
    sql = "SELECT MAX(postid) FROM posts"
    largest = connection.execute(sql).fetchone()['MAX(postid)']
    if postid_url_slug > largest or postid_url_slug < smallest:
        con_dict = {
          "message": "Not Found",
          "status_code": 404
        }
        return jsonify(**con_dict), 404

    sql = "SELECT * FROM posts WHERE postid=?"
    ins = connection.cursor()
    ins.execute(sql, (postid_url_slug,))
    post_info = ins.fetchall()
    sql = "SELECT filename FROM users WHERE username=?"
    ins.execute(sql, (post_info[0]['owner'],))
    filename = ins.fetchall()[0]['filename']
    context = {
        "age": post_info[0]['created'],
        "img_url": '/uploads/' + post_info[0]['filename'],
        "owner": post_info[0]['owner'],
        "owner_img_url": '/uploads/' + filename,
        "owner_show_url": '/u/' + post_info[0]['owner'] + '/',
        "post_show_url": '/p/' + str(postid_url_slug) + '/',
        "url": request.path
    }
    return jsonify(**context)
