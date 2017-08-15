import {connect} from 'react-redux';
import root_actions from 'actions/root_actions';
import New_task_progress from 'components/fragments/New_task_progress';
import {push} from 'react-router-redux';

const mapStateToProps = (state)=>{
  return {
     progress_task_list:state.tasks.progress_task_list
  }
}

const mapDispatchToProps = (dispatch)=>{
  return{
    fetchProgressTask:()=>{
      // dispatch(root_actions.requestProgressTask());
    },
    toResult:(task_id, task_name)=>{
      dispatch(push(`/home/ch/new/result/${task_id}/${task_name}`));
    }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(New_task_progress);
