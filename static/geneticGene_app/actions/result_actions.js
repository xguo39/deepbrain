import {server_domain, apis} from 'base.config';
const user_name = document.getElementById('user_name').innerHTML;

const result_data_actions={
  REQUEST_RESULT_DATA:'REQUEST_RESULT_DATA',
  FETCH_RESULT_DATA_SUCCESS:'FETCH_RESULT_DATA_SUCCESS',
  FETCH_RESULT_DATA_FAILURE:'FETCH_RESULT_DATA_FAILURE',
  UPDATE_DATA_SUCCESS:'UPDATE_DATA_SUCCESS',
  CLEAR_RESULT_DATA:'CLEAR_RESULT_DATA',

  requestResultData:()=>{
    return {
      type:result_actions.REQUEST_RESULT_DATA
    }
  },

  fetchResultDataSuccess:(result_data)=>{
    return{
      type:result_actions.FETCH_RESULT_DATA_SUCCESS,
      payload:result_data
    }
  },

  fetchResultDataFailure:(errCode)=>{
    return{
      type:result_actions.FETCH_RESULT_DATA_FAILURE,
      payload:errCode
    }
  },

  updateDataSuccess(){
    return {
      type:result_actions.UPDATE_DATA_SUCCESS
    }
  },

  clearResultData(){
    return {
      type:result_actions.CLEAR_RESULT_DATA
    }
  },

  fetchResultData:(task_id)=>{
    return (dispatch)=>{
      dispatch(result_actions.requestResultData());
      var option = {
        method:'GET'
      }
      return fetch(server_domain + apis.fetch_case_result + `${task_id}/${user_name}/`, option)
      .then(res=>{
        return res.json();
      })
      .then(data=>{
        if(data.success){
          dispatch(result_actions.fetchResultDataSuccess(data.result_data));
        }else{
          dispatch(result_actions.fetchResultDataFailure(errcode));
        }
      })
    }
  },

}

const check_annotation_actions={
  REQUEST_CHECK_ANNOTATION:'REQUEST_CHECK_ANNOTATION',
  CHECK_ANNOTATION_SUCCESS:'CHECK_ANNOTATION_SUCCESS',
  CHECK_ANNOTATION_FAILURE:'CHECK_ANNOTATION_FAILURE',
  CLEAR_ANNOTATION:'CLEAR_ANNOTATION',


  requestCheckAnnotation:()=>{
    return {
      type:result_actions.REQUEST_CHECK_ANNOTATION
    }
  },
  checkAnnotationSuccess:(annotation_data)=>{
    return {
      type:result_actions.CHECK_ANNOTATION_SUCCESS,
      payload:annotation_data
    }
  },
  checkAnnotationFailure:(errCode)=>{
    return {
      type:result_actions.CHECK_ANNOTATION_FAILURE,
      payload:errCode
    }
  },
  checkAnnotation:(task_id, gene_name, cDNA)=>{
    return (dispatch)=>{
      dispatch(result_actions.requestCheckAnnotation());
      let data = new FormData();
      data.append('cDNA',cDNA);
      let option = {
        method:'POST',
        body:data
      }
      return fetch(server_domain + apis.check_annotation + `${task_id}/${gene_name}/${user_name}/`, option)
      .then(res=>{
        return res.json()
      })
      .then(data=>{
        console.log('this is annotation data');
        console.log(data);
        if(data.success){
          dispatch(result_actions.checkAnnotationSuccess(data.result_detail));
        }else{
          dispatch(result_actions.checkAnnotationFailure(data.errCode));
        }
      })
    }
  },

  clearAnnotation:()=>{
    return {
      type:result_actions.CLEAR_ANNOTATION
    }
  }


}

const review_actions={

}

const result_actions={
  ...result_data_actions,
  ...check_annotation_actions,
  ...review_actions
}

export default result_actions;
