import {connect} from 'react-redux';
import root_actions from 'actions/root_actions';
import Review_list from 'components/modules/Review_list.jsx';
import {push} from 'react-router-redux';

const mapStateToProps = (state)=>{
  return {

  }
}

const mapDispatchToProps = (dispatch)=>{
  return{
    toResult:(task_id, task_name)=>{
      dispatch(push(`/home/ch/new/result/${task_id}/${task_name}`));
    }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Review_list);
