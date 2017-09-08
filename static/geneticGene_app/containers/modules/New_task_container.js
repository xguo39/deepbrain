import {connect} from 'react-redux';
import root_actions from 'actions/root_actions';
import New_task from 'components/modules/New_task.jsx';
import {push} from 'react-router-redux';

const mapStateToProps = (state)=>{
  return {

  }
}

const mapDispatchToProps = (dispatch)=>{
  return{
    toResult:(task_id)=>{
      dispatch(push(`/home/ch/result/${task_id}`));
    }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(New_task);
