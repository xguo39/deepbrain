import {combineReducers} from 'redux';
import {routerReducer} from 'react-router-redux';
import tasks from './task_reducer';

const root_reducer = combineReducers({
  user_name:getUserName,
  tasks,
  router:routerReducer
})
export default root_reducer;

function getUserName(){
  return document.getElementById('user_name').innerHTML;
}
