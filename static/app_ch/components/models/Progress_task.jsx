import React from 'react';
import {static_image} from 'base.config';

// Mapping the status to a percentage
const mappingDict = {

}

class Processing_task extends React.Component{
  constructor(props){
    super(props);
  }

  render(){
    // const current_percent = mappingDict[this.props.task_info.status];
    const current_percent = '50%';
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
        <p className='processing-info'> {this.props.task_info.status} </p>
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
      <div className='completed_task' alt={`${this.props.task_info.id},${this.props.task_info.task_name}`}>
        <span>{this.props.task_info.task_name}</span><span>  完成</span>
        <img src={static_image+'finish_logo.png'} alt='finish_logo'/>
      </div>
    )
  }
}

export {Processing_task, Completed_task};
