import React from 'react';
import ReactDOM from 'react-dom';
import Posts from './posts';

// This method is only called once
ReactDOM.render(
  // Insert the likes component into the DOM
  <div>
    <Posts url="/api/v1/p/" />
  </div>, document.getElementById('reactEntry'),
);
