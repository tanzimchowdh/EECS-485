"""Insta485 logout URLs include: /accounts/logout."""

from flask import (
    redirect,
    session,
    url_for
)
import insta485


@insta485.app.route('/accounts/logout/', methods=['POST'])
def show_logout():
    """Display logout route."""
    session.pop('user_id', None)
    return redirect(url_for('show_login'))
