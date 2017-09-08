import {connect} from 'react-redux';
import root_actions from 'actions/root_actions';
import New_task_upload from 'components/fragments/New_task_upload';
import {push} from 'react-router-redux';

const mapStateToProps = (state)=>{
  return {

  }
}

const mapDispatchToProps = (dispatch)=>{
  return{
    submit_task:(task_data)=>{
      dispatch(root_actions.uploadTask(task_data));
    }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(New_task_upload);
