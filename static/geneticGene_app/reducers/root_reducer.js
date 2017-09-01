import {combineReducers} from 'redux';
import {routerReducer} from 'react-router-redux';
import tasks from './task_reducer';
import results from './result_reducer';

const root_reducer = combineReducers({
  tasks,
  results,
  router:routerReducer
})
export default root_reducer;

function getUserName(){
  return document.getElementById('user_name').innerHTML;
}
