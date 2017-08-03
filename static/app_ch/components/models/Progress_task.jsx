import React from 'react';

class Processing_task extends React.Component{
  constructor(props){
    super(props);
  }

  render(){
    let barStyle={
      "width":"50%",
    }
    return (
      <div>
        <p className='task-title'>任务名称1：80%</p>
        <div className="progress">
          <div className="progress-bar progress-bar-info" role="progressbar" aria-valuenow="50"
          aria-valuemin="0" aria-valuemax="100" style={{"width":"50%"}}>
            <span className="sr-only">50% Complete</span>
          </div>
        </div>
        <p className='processing-info'> 正在处理某个基因 </p>
      </div>
    )
  }
}

class Completed_task extends React.Component{
  constructor(props){
    super(props);
  }

  render(){
    return (
      <div className='completed_text'>
        <span>任务名称</span><span>  完成</span>
      </div>
    )
  }
}

export {Processing_task, Completed_task};
