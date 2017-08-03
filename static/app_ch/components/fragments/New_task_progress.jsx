import React from 'react';
import {Processing_task, Completed_task} from 'components/models/Progress_task.jsx';

class New_task_progress extends React.Component {
  constructor(props){
    super(props);
  }

  _loadProgressList(progress_list){
    return progress_list.map((task, index)=>{
      if(index%2 === 0){
        return <div key={index} className='td3 td-stripe'>
          <Processing_task />
        </div>
      }else{
        return <div key={index} className='td3 '>
          <Completed_task />
        </div>
      }

    })
  }

  render(){
    return (
      <div className='new_task_progress'>
         <div className='tb-title'>上传列表:</div>
         {this._loadProgressList(this.props.progress_list)}
      </div>
    )
  }
}

New_task_progress.propTypes={
  progress_list:React.PropTypes.array
}

New_task_progress.defaultProps={
  progress_list:[1,1,1]
}

export default New_task_progress;
