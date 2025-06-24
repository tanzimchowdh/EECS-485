import React from 'react';
import moment from 'moment';
import PropTypes from 'prop-types';

class Picture extends React.Component {
  /* Display number of likes and like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      age: '', imgUrl: '', owner: '', ownerImgUrl: '', ownerShowUrl: '', postShowUrl: '',
    };
    this.handleChange = this.handleChange.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    // Call REST API to get comments on post
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          age: data.age,
          imgUrl: data.img_url,
          owner: data.owner,
          ownerImgUrl: data.owner_img_url,
          ownerShowUrl: data.owner_show_url,
          postShowUrl: data.post_show_url,
        });
      })
      .catch((error) => console.log(error));
  }

  handleChange() {
    const { lognameLikesThis } = this.props;
    if (!lognameLikesThis) {
      const { likeOrUnlike } = this.props;
      likeOrUnlike();
    }
  }

  render() {
    const {
      age, imgUrl, owner, ownerImgUrl, ownerShowUrl, postShowUrl,
    } = this.state;
    const topBar = {
      textAlign: 'left',
    };
    const timestampStyle = {
      float: 'right',
    };
    return (
      <div style={topBar}>
        <a href={ownerShowUrl}>
          <img src={ownerImgUrl} width="50" alt={owner} />
          {owner}
        </a>
        <span>
          <a href={postShowUrl} style={timestampStyle}>
            {moment.utc(age).fromNow()}
          </a>
        </span>
        <img src={imgUrl} width="600" alt="post" onDoubleClick={this.handleChange} />
      </div>
    );
  }
}

Picture.propTypes = {
  url: PropTypes.string.isRequired,
  likeOrUnlike: PropTypes.func.isRequired,
  lognameLikesThis: PropTypes.bool.isRequired,
};

export default Picture;
