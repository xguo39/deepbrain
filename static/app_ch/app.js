import React from 'react';
import ReactDOM from 'react-dom';
import {Provider} from 'react-redux';
import { Route, Link} from 'react-router-dom';
import { ConnectedRouter, routerMiddleware } from 'react-router-redux';
import 'styles/root_style.scss';

// Import redux store
import {store, history} from 'reducers/store.js';

// Import the main elements
import Top_navbar from 'components/modules/Top_navbar.jsx';
import Main_area from 'containers/modules/Main_area_container';

// Render the element into dom
ReactDOM.render(
  <Provider store = {store}>
    <ConnectedRouter history = {history}>
      <div>
          <Route path='/home/ch' component = {Top_navbar} />
          <Route path='/home/ch' component = {Main_area}/>
      </div>
   </ConnectedRouter>
 </Provider>,
  document.getElementById('root')
)
