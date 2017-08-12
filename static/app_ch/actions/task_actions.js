import {server_domain, apis} from 'base.config';

const upload_task_actions = {
  REQUEST_UPLOAD_TASK:'REQUEST_UPLOAD_TASK',
  UPLOAD_TASK_SUCCESS:'UPLOAD_TASK_SUCCESS',
  UPLOAD_TASK_FAILURE:'UPLOAD_TASK_FAILURE',

  requestUploadTask:()=>{
    return {
      type: task_actions.REQUEST_UPLOAD_TASK
    }
  },

  uploadTaskSuccess:(progress_task_list)=>{
    return {
      type: task_actions.UPLOAD_TASK_SUCCESS,
      payload:progress_task_list
    }
  },

  uploadTaskFailure:(errCode)=>{
    return {
      type:task_actions.UPLOAD_TASK_FAILURE,
      payload:errCode
    }
  },

  // Upload new task with form data
  uploadTask:(taskData)=>{
    return (dispatch)=>{
      dispatch(task_actions.requestUploadTask());
      var option = {
        method:'POST',
        body:taskData
      }
      return fetch(server_domain + apis.upload_task, option)
      .then(res=>res.json())
      .then(data=>{
        console.log(data);
        if(data.success == 'success'){
          dispatch(task_actions.uploadTaskSuccess(data.progress_task_list));
        }else{
          dispatch(task_actions.uploadTaskFailure(errCode));
        }
      })
    }
  }

}


const progress_task_actions = {
  REQUEST_PROGRESS_TASK:'REQUEST_PROGRESS_TASK',

}

const all_task_actions = {
  REQUEST_ALL_TASK:'REQUEST_ALL_TASK',
}

const task_actions = {
  ...upload_task_actions,
  ...progress_task_actions,
  ...all_task_actions
}

export default task_actions;
