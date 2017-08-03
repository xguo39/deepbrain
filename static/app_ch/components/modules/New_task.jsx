import React from 'react';
import New_task_upload from 'components/fragments/New_task_upload.jsx';
import New_task_progress from 'components/fragments/New_task_progress.jsx';


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
