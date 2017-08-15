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
        id:1,
        task_name: 'xiaonan',
        status:'正在处理xxx基因',
        processed_time:'5分钟',
        checked: false
     },
     {
       id:2,
       task_name:'tianqi',
       status:'success',
       processed_time:'4分钟',
       checked:false
     },
    ],
    all_task_list:[
      {
       id:1,
       task_name:"xiaonan",
       pub_date: '2017-06-18, 12:03pm',
       status:'success',
       processed_time:'0',
       checked:false
      },
      {
       id:2,
       task_name:"tianqi",
       pub_date: '2017-06-18, 12:03pm',
       status:'xxxxxxxx fail',
       processed_time:'0',
       checked:true
      }
    ]
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
