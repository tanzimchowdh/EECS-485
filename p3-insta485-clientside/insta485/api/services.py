"""REST API for list of services available."""
import insta485


@insta485.app.route('/api/v1/', methods=["GET"])
def get_services():
    """Return a list of services available."""
    context = {
        "posts": "/api/v1/p/",
        "url": insta485.flask.request.path
    }
    return insta485.flask.jsonify(**context)
