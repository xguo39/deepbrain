import {connect} from 'react-redux';
import root_actions from 'actions/root_actions';
import Task_list from 'components/modules/Task_list.jsx';
import {push} from 'react-router-redux';

const mapStateToProps = (state)=>{
  return {

  }
}

const mapDispatchToProps = (dispatch)=>{
  return{
    toResult:(task_id,task_name)=>{
      dispatch(push(`/home/ch/result/${task_id}/${task_name}`));
    }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Task_list);
