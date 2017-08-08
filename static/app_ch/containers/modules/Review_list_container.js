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
    toResult:(task_id)=>{
      dispatch(push(`/home/ch/result/${task_id}`));
    }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Review_list);
