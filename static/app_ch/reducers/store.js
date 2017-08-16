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
        status:'Annotating variants using genomic databases',
        processed_time:'5分钟',
        checked: false,
     },
     {
       id:2,
       task_name:'tianqi',
       status:'succeed',
       processed_time:'4分钟',
       checked:false,
     },
     {
       id:3,
       task_name:'huihuihui',
       status:'xxxxx failed',
       processed_time:'2分钟',
       checked:false,
     }
    ],
    all_task_list:[
      {
       id:1,
       task_name:"xiaonan",
       pub_date: '2017-06-18, 12:03pm',
       status:'succeed',
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
  },
  results:{
    isFetching:false,
    result_data:{
      summary_table_data:[
         {
           gene:'WWOX',
           transcript:'chr16:g.78466583C>G',
           variant:'c.5354G&t>A',
           protein:'danbaizhi',
           id:'2313fsfsf',
           zygosity:'peixing',
           correlated_phenotypes:'biaoxingpipei',
           pheno_match_score:39,
           hit_criteria:"PM2|BP4",
           pathogenicity:'Uncertain Significance',
           pathogenicity_score:0.88,
           final_score:1.8
         },
         {
           gene:'WNT7A',
           transcript:'chr3:g.13896304C>T',
           variant:'c.5224G&t>C',
           protein:'danbaizhi',
           zygosity:'peixing',
           correlated_phenotypes:'biaoxingpipei',
           pheno_match_score:45,
           hit_criteria:"PM2|BP4",
           pathogenicity:'Uncertain Significance',
           pathogenicity_score:1.28,
           final_score:1.1
         }
      ],
      incidental_table_data:[
        {
          // gene:'WWOX',
          // transcript:'chr16:g.78466583C>G',
          // variant:'GCGTG',
          // protein:'danbaizhi',
          // zygosity:'peixing',
          // pheno_match_score:39,
          // hit_criteria:"PM2|BP4",
          // pathogenicity:'Uncertain Significance',
        },
        {
          // gene:'Shio OM4',
          // transcript:'chr16:g.78466583C>G',
          // variant:'GCGTG',
          // protein:'danbaizhi',
          // zygosity:'peixing',
          // pheno_match_score:88,
          // hit_criteria:"PM2|BP4",
          // pathogenicity:'Uncertain Significance',
        }
      ],
      candidate_table_data:[
        {
          // gene:'WWOX',
          // transcript:'chr16:g.78466583C>G',
          // cDNA:'GCGTG',
          // protein:'danbaizhi',
          // zygosity:'peixing',
          // correlated_phenotypes:'from paper'
        },
        {
          // gene:'Shio OM4',
          // transcript:'chr16:g.78466583C>G',
          // cDNA:'GCGTG',
          // protein:'danbaizhi',
          // zygosity:'peixing',
          // correlated_phenotypes:'from paper'
        }
      ],
      input_gene_data:[
        {
          // Gene:'PPTERER',
          // HGVS_cDNa:'fdsfdsfdsfsdf'
        },
        {
          // Gene:'PPTdsfdfERER',
          // HGVS_cDNa:'fdsfdsfdsfdsfdsfsdf'
        }
      ],
      interpretation_data:[
        {
          // gene:'WWT7',
          // variant:'dsfsdfsf',
          // criteria:'dfsfsdfsdf',
          // interpretation:''
        },
      ]
    },
    annotation_data:[
      {
        criteria:'变异注释',
        interpretation:'xxooxoxoxoxoxoodfdsfdsfdsfdsfdfdsf'
      },
      {
        criteria:'PVS1',
        interpretation:'yykkdfdfsdfdsfsdfdsfsdfsdfsdfjfjdsfdksnflkndf'
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
