let domain;
(()=>{
  const url = window.location.href;
  const pathname = window.location.pathname;
  domain = url.replace(pathname,'');
})()

const basic_info = {
  // static_image:'http://127.0.0.1:8000/static/app_ch/files/images/'
  static_image:`${domain}/static/geneticGene_app/files/images/`
}


const server_domain = `${domain}`;
const static_image = `${domain}/static/geneticGene_app/files/images/`;
const static_files = `${domain}/static/geneticGene_app/files/`;

const apis={
  upload_task:'/api/task/new_task/',
  progress_task_list:'/api/task/progress_task_list/',
  all_task_list:'/api/task/all_task_list/',
  checked_change:'/api/task/task_check/',
  fetch_case_result:'/api/result/',
  check_annotation:'/api/result/'
}


export {static_files, static_image, server_domain, apis};
export default basic_info;
