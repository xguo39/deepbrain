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
    progress_task_list:[],
    all_task_list:[
      // {
      //  id:1,
      //  task_name:"xiaonan",
      //  pub_date: '2017-06-18, 12:03pm',
      //  status:'succeed',
      //  processed_time:'0',
      //  checked:false
      // },
    ]
  },
  results:{
    isFetching:false,
    received_new_data:false,
    review_data:[],
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
      incidental_table_data:[],
      candidate_table_data:[],
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
          gene:'WWT7',
          variant:'dsfsdfsf',
          criteria:'dfsfsdfsdf',
          interpretation:"突变类型: missense_variant.<br/>蛋白功能区: NAD(P)-binding domain.<br/>HGVS ID: chr16:g.78466583C>G.<br/>RefSeq ID: <a href=' '> rs117209694 </a ><br/>蛋白质: p.Asn330Lys.<br/>外显子: 8.<br/>GeneCards: <a href='http://www.genecards.org/cgi-bin/carddisp.pl?gene=WWOX'> WWOX </a ><br/>OMIM: <a href='https://www.omim.org/entry/605131'> 605131 </a ><br/>Decipher: <a href='https://decipher.sanger.ac.uk/search?q=WWOX#consented-patients/results'> WWOX </a ><br/>Genetics Home Reference: <a href='https://ghr.nlm.nih.gov/gene/WWOX'> WWOX </a ><br/>GeneReviews: <a href='https://www.ncbi.nlm.nih.gov/books/NBK1116/?term=WWOX'> WWOX </a ><br/>ExAC 最小等位基因频率(MAF): 0.000174 (<a href='http://exac.broadinstitute.org/variant/16-78466583-C-G'> 16-78466583-C-G </a >)<br/>ExAC 最小等位基因频率(MAF)详细数据: Total Allele Count (21), Total Allele Number (120722), Allele Frequency for all races (0.0002), Number of Homozygotes (0), Homozygotes Percentage (0.0000), African Allele Count (1), African Allele Number (9796), African Allele Frequency (0.0001), Latino Allele Count (0), Latino Allele Number (11570), Latino Allele Frequency (0.0000), East Asian Allele Count (0), East Asian Allele Number (8622), East Asian Allele Frequency (0.0000), European (Finnish) Allele Count (0), European (Finnish) Allele Number (6612), European (Finnish) Allele Frequency (0.0000), European (Non-Finnish) Allele Count (20), European (Non-Finnish) Allele Number (66710), European (Non-Finnish) "
        },
      ]
    },
    annotation_data:[
      {
        criteria:'lalal',
        interpretation:'fsdfsdfs'
      }
    ]
  },

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
