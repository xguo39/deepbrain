import {connect} from 'react-redux';
import root_actions from 'actions/root_actions';
import Task_list from 'components/modules/Task_list.jsx';
import {push} from 'react-router-redux';

const mapStateToProps = (state)=>{
  return {
    task_list:state.tasks.all_task_list
  }
}

const mapDispatchToProps = (dispatch)=>{
  return{
    toResult:(task_id,task_name)=>{
      dispatch(push(`/home/ch/new/result/${task_id}/${task_name}`));
    },
    fetchTaskList:()=>{
      dispatch(root_actions.fetchTaskList());
    }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Task_list);
