import React from 'react';
import PropTypes from 'prop-types';

class Likes extends React.Component {
  /* Display number of likes and like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.handleChange = this.handleChange.bind(this);
  }

  handleChange() {
    const { likeOrUnlike } = this.props;
    likeOrUnlike();
  }

  render() {
    // This line automatically assigns this.state.numLikes to the const variable numLikes
    const { numLikes } = this.props;
    const { lognameLikesThis } = this.props;

    // Render number of likes
    return (
      <div className="likes">
        <p>
          {numLikes}
          {' '}
          like
          {numLikes !== 1 ? 's' : ''}
        </p>
        <button type="button" className="like-unlike-button" onClick={this.handleChange}>
          {lognameLikesThis ? 'Unlike' : 'Like'}
        </button>
      </div>
    );
  }
}

Likes.propTypes = {
  numLikes: PropTypes.number.isRequired,
  lognameLikesThis: PropTypes.bool.isRequired,
  likeOrUnlike: PropTypes.func.isRequired,
};

export default Likes;
