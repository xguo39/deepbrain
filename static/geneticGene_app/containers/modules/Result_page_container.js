import {connect} from 'react-redux';
import root_actions from 'actions/root_actions';
import Result_page from 'components/modules/Result_page.jsx';
import {push, go} from 'react-router-redux';

const mapStateToProps = (state)=>{
  return {
    isFetching:state.results.isFetching,
    result_data:state.results.result_data,
    received_new_data:state.results.received_new_data
  }
}

const mapDispatchToProps = (dispatch)=>{
  return{
     goBack:()=>{
       dispatch(go(-1));
     },

     fetchResultData:(task_id)=>{
       dispatch(root_actions.fetchResultData(task_id));
     },

     updateDataFinish:()=>{
       dispatch(root_actions.updateDataSuccess());
     },

     showAnnotation:(current_path, gene, cDNA)=>{
       dispatch(push(`${current_path}/${gene}/${cDNA}`));
     },

     clearResultData:()=>{
       dispatch(root_actions.clearResultData());
     }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Result_page);
