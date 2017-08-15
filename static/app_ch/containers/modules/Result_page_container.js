import {connect} from 'react-redux';
import root_actions from 'actions/root_actions';
import Result_page from 'components/modules/Result_page.jsx';
import {push, go} from 'react-router-redux';

const mapStateToProps = (state)=>{

  return {

  }
}

const mapDispatchToProps = (dispatch)=>{
  return{
     goBack:()=>{
       dispatch(go(-1));
     },

     

     showAnnotation:(current_path, gene, transicript)=>{
       dispatch(push(`${current_path}/${gene}`));
     }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Result_page);
