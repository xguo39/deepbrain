const basic_info = {
  static_image:'http://127.0.0.1:8000/static/app_ch/files/images/'
}

const server_domain = 'http://127.0.0.1:8000';
const static_image = 'http://127.0.0.1:8000/static/app_ch/files/images/';

const apis={
  upload_task:'/api/task/new_task/',
  progress_task_list:'/api/task/progress_task_list/',
  all_task_list:'/api/task/all_task_list/',
  checked_change:'/api/task/task_check/',
  fetch_case_result:'/api/result/',
  check_annotation:'/api/result/'
}


export {static_image, server_domain, apis};
export default basic_info;
