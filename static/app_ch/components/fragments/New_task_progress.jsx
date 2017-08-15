import React from 'react';
import {Processing_task, Completed_task} from 'components/models/Progress_task.jsx';

class New_task_progress extends React.Component {
  constructor(props){
    super(props);
  }

  componentWillMount(){
    this.props.fetchTaskList();
  }

  _handleClick(evt){
    let target = evt.target;
    if(target.className.indexOf('completed_task')!==-1){
      const task_info = target.getAttribute('alt').split(',');
      const task_id = parseInt(task_info[0]);
      const task_name = task_info[1];
      this.props.toResult(task_id, task_name);
    };
  }

  _loadProgressList(progress_list){
    return progress_list.map((task, index)=>{
      let status = task.status;
      if(status!=='succeed'){
        return <div key={index} className='td3 td-stripe'>
          <Processing_task task_info={task}/>
        </div>
      }else{
        return <div key={index} className='td3'>
          <Completed_task task_info={task}/>
        </div>
      }
    })
  }

  render(){
    return (
      <div className='new_task_progress' onClick={(evt)=>this._handleClick(evt)}>
         <div className='tb-title'>上传列表:</div>
         {this._loadProgressList(this.props.progress_task_list)}
      </div>
    )
  }
}

New_task_progress.propTypes={
  progress_task_list:React.PropTypes.array,
  fetchTaskList:React.PropTypes.func,
  toResult:React.PropTypes.func,
}

New_task_progress.defaultProps={
  progress_task_list:[],
  fetchTaskList:()=>{},
  toResult:()=>{}
}

export default New_task_progress;
