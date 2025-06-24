import React from 'react';
import PropTypes from 'prop-types';

class Comments extends React.Component {
  /* Display comments and comment form for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { comments: [], value: '' };
    // this.leaveComment = this.leaveComment.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
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
          comments: data.comments,
        });
      })
      .catch((error) => console.log(error));
  }

  handleChange(event) {
    this.setState({ value: event.target.value });
  }

  handleSubmit(event) {
    // alert('A name was submitted: ' + this.state.value);
    event.preventDefault();
    const { url } = this.props;
    const { comments } = this.state;
    const { value } = this.state;
    const tempComments = comments;
    const jsonData = { text: value };
    fetch(url, {
      credentials: 'same-origin', method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(jsonData),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        tempComments.push(data);
        this.setState({
          comments: tempComments,
          value: '',
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    // This line automatically assigns this.state.numLikes to the const variable numLikes
    const { comments } = this.state;
    const { value } = this.state;
    // let value = this.state;
    // Render number of likes
    const paragraphs = comments.map((comment) => (
      <p key={comment.commentid}>
        <a href={comment.owner_show_url}>
          {comment.owner}
        </a>
        <span> </span>
        {comment.text}
      </p>
    ));
    return (
      <div className="comments">
        {paragraphs}
        <form className="comment-form" onSubmit={this.handleSubmit}>
          <input type="text" value={value} onChange={this.handleChange} />
        </form>
      </div>
    );
  }
}

Comments.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Comments;
