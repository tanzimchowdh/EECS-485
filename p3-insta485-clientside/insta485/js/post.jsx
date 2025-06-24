import React from 'react';
import PropTypes from 'prop-types';
import Likes from './likes';
import Comments from './comments';
import Picture from './post_image';

class Post extends React.Component {
  /* Display number of likes and like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { numLikes: 0, lognameLikesThis: false };
    this.likeOrUnlike = this.likeOrUnlike.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;
    let likesUrl = url;
    likesUrl += 'likes/';
    // Call REST API to get comments on post
    fetch(likesUrl, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        let lognameLikes = true;
        if (data.logname_likes_this === 0) {
          lognameLikes = false;
        }
        this.setState({
          numLikes: data.likes_count,
          lognameLikesThis: lognameLikes,
        });
      })
      .catch((error) => console.log(error));
  }

  likeOrUnlike() {
    const { url } = this.props;
    let likesUrl = url;
    likesUrl += 'likes/';
    const { lognameLikesThis } = this.state;
    const { numLikes } = this.state;
    if (lognameLikesThis) {
      fetch(likesUrl, { credentials: 'same-origin', method: 'DELETE' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .then(this.setState({
          numLikes: numLikes - 1,
          lognameLikesThis: !lognameLikesThis,
        }))
        .catch((error) => console.log(error));
    } else {
      fetch(likesUrl, { credentials: 'same-origin', method: 'POST' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .then(this.setState({
          numLikes: numLikes + 1,
          lognameLikesThis: !lognameLikesThis,
        }))
        .catch((error) => console.log(error));
    }
  }

  render() {
    const { url } = this.props;
    let commentsUrl = url;
    const { numLikes } = this.state;
    const { lognameLikesThis } = this.state;
    commentsUrl += 'comments/';
    const postStyle = {
      border: 'solid',
      width: '600px',
      margin: 'auto',
    };
    return (
      <div style={postStyle}>
        <Picture url={url} likeOrUnlike={this.likeOrUnlike} lognameLikesThis={lognameLikesThis} />
        <Likes
          numLikes={numLikes}
          lognameLikesThis={lognameLikesThis}
          likeOrUnlike={this.likeOrUnlike}
        />
        <Comments url={commentsUrl} />
      </div>
    );
  }
}
Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;
