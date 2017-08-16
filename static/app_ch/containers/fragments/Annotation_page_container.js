import {connect} from 'react-redux';
import root_actions from 'actions/root_actions';
import Annotation_page from 'components/fragments/Annotation_page';
import {push,go} from 'react-router-redux';

const mapStateToProps = (state)=>{
  return {

  }
}

const mapDispatchToProps = (dispatch)=>{
  return{
    goBack:()=>{
      dispatch(go(-1));
    },
    fetchAnnotation:(gene_name, cDNA)=>{
      console.log(gene_name);
    }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Annotation_page);
