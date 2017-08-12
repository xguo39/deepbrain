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
    isFetching:false,
    progress_task_list:[
     {
        task_id:1,
        task_name: 'xiaonan',
        completed_missons: 8,
        total_missions: 10,
        current_misson:'正在处理xxx基因',
        estimated_time:'5分钟',
        checked: false
     },
     {
       task_id:2,
       task_name:'tianqi',
       completed_missons:10,
       total_missions:10,
       current_mission:'',
       estimated_time:'4分钟',
       checked:false
     },
    ],
    all_task_list:[]
  }
};

//create a history of choosing
const history = createHistory();
// Create redux store with middleware
const logger = createLogger();
const routeMiddleware  = routerMiddleware(history);
const createStoreWithMiddleware = applyMiddleware(thunk, logger, routeMiddleware)(createStore);

const store = createStoreWithMiddleware(root_reducer,initialState);


export {store, history};
export default store;
