import React from 'react';

class Top_navbar extends React.Component{
  constructor(props){
      super(props);
      this.state = {
        user_name:document.getElementById('user_name').innerHTML
      }
  }

  render(){
    return (
      <nav className='navbar navbar-default fixed-top'>
        <div className='container-fluid'>
          <div className="navbar-header">
            <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
              <span className="sr-only">Toggle navigation</span>
              <span className="icon-bar"></span>
              <span className="icon-bar"></span>
              <span className="icon-bar"></span>
            </button>
            <a className="navbar-brand" href=""><small>诺亚医生 | 遗传病基因智能解读 Beta</small></a>
          </div>

          <div className="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
            <ul className="nav navbar-nav navbar-right">
              <li className="dropdown">
                <a href="" className="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false">语言<span className="caret"></span></a>
                <ul className="dropdown-menu" role="menu">
                  <li><a href="">English</a></li>
                  <li><a href="">中文</a></li>
                </ul>
              </li>

              <li className="dropdown">
                <a href="#" className="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false">账户 <span className="caret"></span></a>
                <ul className="dropdown-menu" role="menu">
                  <li><a href="">用户名:{`${this.state.user_name}`}</a></li>
                  <li className="divider"></li>
                  <li><a href='/password/change/'>修改密码</a></li>
                  <li><a href='/logout/'>退出登陆</a></li>
                </ul>
              </li>

            </ul>
          </div>

        </div>
      </nav>
    )
  }
}

Top_navbar.propTypes={

}

Top_navbar.defaultProps={

}

export default Top_navbar;
