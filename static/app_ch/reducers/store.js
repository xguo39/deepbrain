import {createStore, applyMiddleware, combineReducers} from 'redux';
import { routerMiddleware, routerReducer } from 'react-router-redux';
import {createLogger} from 'redux-logger';
import createHistory from 'history/createBrowserHistory';
import thunk from 'redux-thunk';

// Import the neccerry root reducer
import root_reducer from './root_reducer';

// Create the initial state
const initialState = {
  tasks:{

  }
};

//create a history of choosing
const history = createHistory();
// Create redux store with middleware
const logger = createLogger();
const routeMiddleware  = routerMiddleware(history);
const createStoreWithMiddleware = applyMiddleware(thunk, routeMiddleware)(createStore);

const store = createStoreWithMiddleware(root_reducer,initialState);


export {store, history};
export default store;
