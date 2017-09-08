import {server_domain, apis} from 'base.config';
const user_name = document.getElementById('user_name').innerHTML;

const upload_task_actions = {

  REQUEST_UPLOAD_TASK:'REQUEST_UPLOAD_TASK',
  UPLOAD_TASK_SUCCESS:'UPLOAD_TASK_SUCCESS',
  UPLOAD_TASK_FAILURE:'UPLOAD_TASK_FAILURE',

  requestUploadTask:()=>{
    return {
      type: task_actions.REQUEST_UPLOAD_TASK
    }
  },

  uploadTaskSuccess:()=>{
    return {
      type: task_actions.UPLOAD_TASK_SUCCESS,
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
      return fetch(server_domain + apis.upload_task+`${user_name}/`, option)
      .then(res=>res.json())
      .then(data=>{
        if(data.success){
          window.location.reload();
          dispatch(task_actions.uploadTaskSuccess());
          // Constanly fetch the progress task list after uploading
          dispatch(task_actions.fetchProgressTask());
        }else{
          alert('十分抱歉，该文件无法处理，可能是由于基因文件未经初筛，或文件内格式有误，请阅读使用说明后再重新上传，谢谢');
          window.location.reload();
          dispatch(task_actions.uploadTaskFailure(data.errCode));
        }
      })
    }
  }

}

const progress_task_actions = {
  REQUEST_PROGRESS_TASK:'REQUEST_PROGRESS_TASK',
  FETCH_PROGRESS_TASK_SUCCESS:'FETCH_PROGRESS_TASK_SUCCESS',
  FETCH_PROGRESS_TASK_FAIL:'FETCH_PROGRESS_TASK_FAIL',

  requestProgressTask:()=>{
    return {
      type:task_actions.REQUEST_PROGRESS_TASK,
    }
  },

  fetchProgressTaskSuccess:(progress_task_list)=>{
    return {
      type:task_actions.FETCH_PROGRESS_TASK_SUCCESS,
      payload:progress_task_list
    }
  },

  fetchProgressTaskFail:(errCode)=>{
    return {
      type:task_actions.FETCH_PROGRESS_TASK_FAIL,
      payload:errCode
    }
  },

  timeout:null,

  fetchProgressTask:()=>{
    return (dispatch)=>{
      dispatch(task_actions.requestProgressTask());
      var option = {
        method:'GET'
      }
      return fetch(server_domain + apis.progress_task_list + `${user_name}/`, option)
      .then(res=>{
        return res.json();
      })
      .then(data=>{
        if(data.success){
          dispatch(task_actions.fetchProgressTaskSuccess(data.list));
          // Constanly checked the progress list
          for(var task of data.list){
            if(task.status !== 'succeed' && task.status.indexOf('failed')===-1){
             task_actions.timeout = setTimeout(()=>dispatch(task_actions.fetchProgressTask()), 5000);
             break;
            }
          }
        }else{
          dispatch(task_actions.fetchProgressTaskFail(data.errcode));
        }
      })
    }
  }

}

const all_task_actions = {
  REQUEST_ALL_TASK:'REQUEST_ALL_TASK',
  FETCH_ALL_TASK_SUCCESS:'FETCH_ALL_TASK_SUCCESS',
  FETCH_ALL_TASK_FAILURE:'FETCH_ALL_TASK_FAILURE',

  requestAllTask:()=>{
    return {
      type:task_actions.REQUEST_ALL_TASK
    }
  },

  fetchAllTaskSuccess:(task_list)=>{
    return {
      type:task_actions.FETCH_ALL_TASK_SUCCESS,
      payload:task_list
    }
  },

  fetchAllTaskFailure:(errCode)=>{
    return {
      type:task_actions.FETCH_ALL_TASK_FAILURE,
      payload:errCode
    }
  },

  // Fetch all task
  fetchTaskList:()=>{
    return (dispatch)=>{
      dispatch(task_actions.requestAllTask());
      var option = {
        method:'GET'
      }
      return fetch(server_domain + apis.all_task_list+`${user_name}/`, option)
      .then(res=>{
        return res.json();
      })
      .then(data=>{
        if(data.success){
          dispatch(task_actions.fetchAllTaskSuccess(data.list));
        }else{
          dispatch(task_actions.fetchAllTaskFailure(data.errcode));
        }
      })
    }
  }

}

const checked_change_actions={
  REQUEST_CHECKED_CHANGE:'REQUEST_CHECKED_CHANGE',
  CHECKED_CHANGE_SUCCESS:'CHECKED_CHANGE_SUCCESS',
  CHECKED_CHANGE_FAILURE:'CHECKED_CHANGE_FAILURE',

  requestCheckedChange:()=>{
    return {
      type:task_actions.REQUEST_CHECKED_CHANGE
    }
  },

  checkedChangeSuccess:()=>{
    return {
      type:task_actions.CHECKED_CHANGE_SUCCESS
    }
  },

  checkedChangeFailure:(errCode)=>{
    return {
      type:task_actions.CHECKED_CHANGE_FAILURE,
      payload:errCode
    }
  },

  checkedChange:(task_id)=>{
    return (dispatch)=>{
      dispatch(task_actions.requestCheckedChange());
      let data = new FormData();
      data.append('task_id', task_id);
      var option = {
        method:'PUT',
        body:data
      }
      return fetch(server_domain + apis.checked_change+`${user_name}/`, option)
      .then(res=>{
        return res.json();
      })
      .then(data=>{
        console.log('this is checked change');
        console.log(data);
        if(data.success){
          dispatch(task_actions.fetchProgressTask())
        }else{
          dispatch(task_actions.checkedChangeFailure(data.errCode));
        }
      })
    }
  }

}

const task_actions = {
  ...upload_task_actions,
  ...progress_task_actions,
  ...all_task_actions,
  ...checked_change_actions
}

export default task_actions;
