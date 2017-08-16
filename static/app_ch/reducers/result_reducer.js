import root_actions from 'actions/root_actions';

export default function results(state={},action){
  switch(action.type){
    case root_actions.REQUEST_RESULT_DATA:
      return {
        ...state,
        isFetching:true
      }

    case root_actions.FETCH_RESULT_DATA_SUCCESS:
      return {
        ...state,
        isFetching:false,
        result_data:action.payload
      }

    case root_actions.FETCH_RESULT_DATA_FAILURE:
      return {
        ...state,
        isFetching:false,
        errCode:action.payload
      }

    case root_actions.REQUEST_CHECK_ANNOTATION:
      return{
        ...state,
        isFetching:true,
      }

    case root_actions.CHECK_ANNOTATION_SUCCESS:
      return {
        ...state,
        isFetching:false,
        annotation_data:action.payload
      }

    case root_actions.CHECK_ANNOTATION_FAILURE:
      return {
        ...state,
        isFetching:false,
        errCode:action.payload
      }

    default:
      return state;
  }
}
