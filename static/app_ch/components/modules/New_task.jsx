import React from 'react';
import New_task_upload from 'containers/fragments/New_task_upload_container';
import New_task_progress from 'containers/fragments/New_task_progress_container';


class New_task extends React.Component {
  constructor(props){
    super(props);
  }

  render(){
    return (
      <div className='new_task'>
        <New_task_upload/>
        <New_task_progress/>
        <label className='btn btn-primary' htmlFor='task_submit'><span>提</span><span>交</span></label>
      </div>
    )
  }
}

New_task.propTypes={

}

New_task.defaultProps={

}

export default New_task;
