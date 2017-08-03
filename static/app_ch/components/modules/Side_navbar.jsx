import React from 'react';
import {
  Link
} from 'react-router-dom';
import {static_image} from 'base.config';

class Side_navbar extends React.Component{
  constructor(props){
    super(props);
  }

  render(){
    return (
      <nav className='col-sm-2 sidebar'>
        <img className='bg' src={static_image + "toolbar-bg.png"} alt='sidebar-bg'></img>
        <div className='bg-filter'></div>
        <ul className='nav flex-column'>
          <li className='nav-item'>
            <Link to='/home/ch/' className='nav-link active'>
              <img src={static_image + "newtask-icon.png"} alt='new_task'></img>
              <span>新任务</span>
            </Link>
          </li>
          <li className='nav-item'>
            <Link to='/home/ch/task_list' className='nav-link'>
              <img src={static_image + "tasklist-icon.png"} alt='task-list'></img>
              <span>任务列表</span>
            </Link>
          </li>
          <li className='nav-item'>
            <Link to='/home/ch/feedback' className='nav-link'>
              <img src={static_image + "feedback-icon.png"} alt='result-review'></img>
              <span>结果评估</span>
            </Link>
          </li>
        </ul>
      </nav>
    )
  }
}

Side_navbar.propTypes={

}

Side_navbar.defaultProps={

}

export default Side_navbar;
