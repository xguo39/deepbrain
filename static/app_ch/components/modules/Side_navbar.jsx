import React from 'react';
import {
  Link
} from 'react-router-dom';
import {static_image} from 'base.config';

class Side_navbar extends React.Component{
  constructor(props){
    super(props);
    this.state={
      active_link:null
    }
  }

  componentDidMount(){

    let pathname = this.props.location.pathname;
    pathname = pathname.substring(pathname.lastIndexOf('/')+1);
    let currentActive;
    switch (pathname) {
      case 'task_list':
        currentActive = document.getElementsByClassName('sidebar-link')[1];
        currentActive.classList.add('active');
        break;

      case 'review_list':
        currentActive = document.getElementsByClassName('sidebar-link')[2];
        currentActive.classList.add('active');
        break;

      default:
        currentActive = document.getElementsByClassName('sidebar-link')[0];
        currentActive.classList.add('active');
        break;
    }

    this.setState({
      active_link:document.getElementsByClassName('nav-link active')[0]
    });
  
  }

  _handleClick(evt){
    // Change the hightlight item
    if(evt.target.nodeName==='A'){
      this.setState({
        active_link: evt.target
      })
    }
  }

  _handleHover(evt){
    if(evt.target.nodeName==='A'){
      document.activeElement.blur();
      let allNav = document.getElementsByClassName('nav-link');
      for(let item of allNav){
        item.classList.remove('active');

      }
      evt.target.classList.add('active');
    }
  }

  _handleLeave(evt){
    if(evt.target === evt.currentTarget){
      let activeOne = document.getElementsByClassName('active')[0];
      activeOne.classList.remove('active');
      this.state.active_link.classList.add('active');
    }
  }

  render(){
    return (
      <nav className='col-sm-2 sidebar'>
        <img className='bg' src={static_image + "toolbar-bg.png"} alt='sidebar-bg'></img>
        <div className='bg-filter'></div>
        <ul className='nav flex-column'
          onClick={(evt)=>this._handleClick(evt)}
          onMouseOver={(evt)=>this._handleHover(evt)}
          onMouseLeave={(evt)=>this._handleLeave(evt)}>
          <li className='nav-item'>
            <Link to='/home/ch/new/' className='nav-link sidebar-link'>
              <img src={static_image + "newtask-icon.png"} alt='new_task'></img>
              <span>新任务</span>
            </Link>
          </li>
          <li className='nav-item'>
            <Link to='/home/ch/new/task_list' className='nav-link sidebar-link'>
              <img src={static_image + "tasklist-icon.png"} alt='task-list'></img>
              <span>任务列表</span>
            </Link>
          </li>
          <li className='nav-item'>
            <Link to='/home/ch/new/review_list' className='nav-link sidebar-link'>
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
