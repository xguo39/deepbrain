import {createStore, applyMiddleware, combineReducers} from 'redux';
import {createLogger} from 'redux-logger';
import thunk from 'redux-thunk';

// Import the neccerry root reducer
import root_reducer from './root_reducer';

// Create the initial state
const initialState = {

};

// Create redux store with middleware
const logger = createLogger();
const createStoreWithMiddleware = applyMiddleware(thunk)(createStore);
const store = createStoreWithMiddleware(root_reducer, initialState);

export default store;
