import {connect} from 'react-redux';
import root_actions from 'actions/root_actions';
import Result_page from 'components/modules/Result_page.jsx';
import {push, go} from 'react-router-redux';

const mapStateToProps = (state)=>{
  return {
    result_data:state.results.result_data
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

     showAnnotation:(current_path, gene, transcript)=>{
       dispatch(push(`${current_path}/${gene}/${transcript}`));
     }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Result_page);
