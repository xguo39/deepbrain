import {combineReducers} from 'redux';
import {routerReducer} from 'react-router-redux';
import tasks from './task_reducer';

const root_reducer = combineReducers({
  tasks,
  router:routerReducer
})
export default root_reducer;
