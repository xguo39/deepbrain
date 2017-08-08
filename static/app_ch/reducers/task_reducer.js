import root_actions from 'actions/root_actions';

export default function tasks(state={}, action){
  switch (action.type){
    case root_actions.REQUEST_UPLOAD_TASK:
     return{
       ...state
     }

    default:
     return state
  }
}
