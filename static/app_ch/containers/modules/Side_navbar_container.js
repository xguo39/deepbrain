import {connect} from 'react-redux';
import {withRouter} from 'react-router-dom';
import root_actions from 'actions/root_actions';
import Side_navbar from 'components/modules/Side_navbar.jsx';
import {push} from 'react-router-redux';

const mapStateToProps = (state)=>{
  return {

  }
}

const mapDispatchToProps = (dispatch)=>{
  return{

  }
}

export default connect(
  mapDispatchToProps
)(Side_navbar);
