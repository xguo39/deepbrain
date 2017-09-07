import root_actions from 'actions/root_actions';

export default function tasks(state={}, action){
  switch (action.type){
    case root_actions.REQUEST_UPLOAD_TASK:
     return{
       ...state,
       isUploading:true
     }

    case root_actions.UPLOAD_TASK_SUCCESS:
     return{
       ...state,
       isUploading:false,
     }

    case root_actions.UPLOAD_TASK_FAILURE:
     return{
       ...state,
       isUploading:false,
       errorCode:action.payload
     }

    case root_actions.REQUEST_ALL_TASK:
      return{
        ...state,
        isFetching:true,
      }

    case root_actions.FETCH_ALL_TASK_SUCCESS:
      return{
        ...state,
        isFetching:false,
        all_task_list:action.payload
      }

    case root_actions.FETCH_ALL_TASK_FAILURE:
      return{
        ...state,
        isFetching:false,
        errCode:action.payload
      }

    case root_actions.REQUEST_PROGRESS_TASK:
      return{
        ...state,
        isFetching:true,
      }

    case root_actions.FETCH_PROGRESS_TASK_SUCCESS:
      return{
        ...state,
        isFetching:false,
        progress_task_list:action.payload
      }

    case root_actions.FETCH_PROGRESS_TASK_FAIL:
      return{
        ...state,
        isFetching:false,
        errCode:action.payload
      }

    case root_actions.REQUEST_CHECKED_CHANGE:
      return{
        ...state,
        isFetching:true
      }

    case root_actions.CHECKED_CHANGE_SUCCESS:
      return{
        ...state,
        isFetching:false
      }

    case root_actions.CHECKED_CHANGE_FAILURE:
      return{
        ...state,
        isFetching:false,
        errCode:action.payload
      }

    default:
     return state
  }
}
