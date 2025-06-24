import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import Post from './post';

class Posts extends React.Component {
  constructor(props) {
    super(props);
    this.state = { nextUrl: this.props, results: [] };
    this.fetchMoreData = this.fetchMoreData.bind(this);
  }

  componentDidMount() {
    const { url } = this.props;
    // Call rest api
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log(data.next);
        this.setState({
          nextUrl: data.next,
          results: data.results,
        });
      })
      .catch((error) => console.log(error));
  }

  fetchMoreData() {
    const { nextUrl } = this.state;
    fetch(nextUrl, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const { results } = this.state;
        this.setState({
          nextUrl: data.next,
          results: results.concat(data.results),
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    const { nextUrl, results } = this.state;
    console.log(nextUrl);
    return (
      <div>
        <InfiniteScroll
          dataLength={results.length}
          next={this.fetchMoreData}
          hasMore={nextUrl !== ''}
        >
          {results.map((result) => (
            <div key={result.postid}>
              <Post url={result.url} />
              <br />
            </div>
          ))}
        </InfiniteScroll>
      </div>
    );
  }
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Posts;
