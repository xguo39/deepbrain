import React from 'react';

class Processing_task extends React.Component{
  constructor(props){
    super(props);
  }

  render(){
    const current_percent = `${this.props.task_info.completed_missons*10}%`;
    let barStyle={
      "width":current_percent,
    }
    return (
      <div>
        <p className='task-title'>{`${this.props.task_info.task_name}：${current_percent}`}</p>
        <div className="progress">
          <div className="progress-bar progress-bar-info" role="progressbar" aria-valuenow="50"
          aria-valuemin="0" aria-valuemax="100" style={barStyle}>
            <span className="sr-only">50% Complete</span>
          </div>
        </div>
        <p className='processing-info'> {this.props.task_info.current_misson} </p>
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
      <div className='completed_task' alt={`${this.props.task_info.task_id},${this.props.task_info.task_name}`}>
        <span>{this.props.task_info.task_name}</span><span>  完成</span>
      </div>
    )
  }
}

export {Processing_task, Completed_task};
