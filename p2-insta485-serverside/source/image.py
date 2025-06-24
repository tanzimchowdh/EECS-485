"""Insta485 image route."""
from flask import (
    session,
    abort,
    send_from_directory
)
import insta485


@insta485.app.route('/uploads/<path:filename>', methods=['GET'])
def show_image(filename):
    """Display /uploads/<path::filename> route."""
    if 'user_id' not in session:
        abort(403, description="Must be logged in")
    return send_from_directory(insta485.app.config['UPLOAD_FOLDER'], filename)
