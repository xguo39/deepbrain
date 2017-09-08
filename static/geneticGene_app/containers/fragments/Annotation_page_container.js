import {connect} from 'react-redux';
import root_actions from 'actions/root_actions';
import Annotation_page from 'components/fragments/Annotation_page';
import {push,go} from 'react-router-redux';

const mapStateToProps = (state)=>{
  return {
     annotation_data:state.results.annotation_data
  }
}

const mapDispatchToProps = (dispatch)=>{
  return{
    goBack:()=>{
      dispatch(go(-1));
    },
    fetchAnnotation:(task_id, gene_name, cDNA)=>{
      dispatch(root_actions.checkAnnotation(task_id, gene_name, cDNA));
    },
    clearAnnotation:()=>{
      dispatch(root_actions.clearAnnotation());
    }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Annotation_page);
