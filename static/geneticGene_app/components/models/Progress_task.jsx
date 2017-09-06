import React from 'react';
import {static_image} from 'base.config';

// Mapping the status to a percentage
const mappingDict = {
 'Preprocessing data for interpretation':'10%', 'generating candidate variants':'20%',
 'Annotating variants using genomic databases':'40%', 'Mapping phenotypes to genes':'40%',
 'Searching biomedical literatures':'55%', 'Checking ACMG standard':'80%', 'Filtering variants based on phenotypes': '90%',
  'succeed':'100%',
}

class Processing_task extends React.Component{
  constructor(props){
    super(props);
  }

  render(){
    const current_percent = mappingDict[this.props.task_info.status];
    let barStyle={
      "width":current_percent,
    }
    return (
      <div>
        <p className='task-title'>{`${this.props.task_info.task_name}：${current_percent}`}</p>
        <div className="progress">
          <div className="progress-bar progress-bar-info progress-bar-striped active" role="progressbar" aria-valuenow="50"
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

class Failed_task extends React.Component{
  constructor(props){
    super(props);
  }

  render(){
    return (
      <div className='failed_task' alt={`${this.props.task_info.id},${this.props.task_info.task_name}`}>
        <span>{this.props.task_info.task_name}</span>
          <span> 上传失败<br/>
           <span className='explain'>可能是文件内格式有误，请重新阅读使用说明，或
           <a href='http://www.genonova.com/#contact' target="_blank">联系我们</a></span>
          </span>
        {/* <img src={static_image+'finish_logo.png'} alt='finish_logo'/> */}
      </div>
    )
  }
}

class Waiting_task extends React.Component{
  constructor(props){
    super(props);
  }

  render(){
    return(
      <div className='waiting_task'>
        <img src={static_image+'loading_sign.gif'} alt='result_loding_sign'></img>
      </div>
    )
  }
}

export {Processing_task, Completed_task, Failed_task, Waiting_task};
