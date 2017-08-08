const upload_task_actions = {
  REQUEST_UPLOAD_TASK:'REQUEST_UPLOAD_TASK',
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
