import task_actions from './task_actions';
import result_actions from './result_actions';

const root_actions = {
  ...task_actions,
  ...result_actions
}

export default root_actions;
