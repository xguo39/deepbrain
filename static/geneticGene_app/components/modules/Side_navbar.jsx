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

        <div className='related_link_block'>
           <p>参考链接</p>
           <a href='https://www.omim.org/' target="_blank">OMIM</a>
           <a href='https://www.ncbi.nlm.nih.gov/clinvar/' target="_blank">ClinVar</a>

           <a href='https://www.ncbi.nlm.nih.gov/books/NBK1116/' target="_blank">GeneReviews</a>
           <a href='http://www.genenames.org/' target="_blank">HGNC</a>

           <a href='http://human-phenotype-ontology.github.io/about.html' target="_blank">HPO</a>
           <a href='http://wiki.chinahpo.org/index.php/%E9%A6%96%E9%A1%B5' target="_blank">中文HPO</a>

           <a href='http://www.acmg.net/docs/Standards_Guidelines_for_the_Interpretation_of_Sequence_Variants.pdf' target="_blank">ACMG</a>
           <a href='http://acmg.cbgc.org.cn/doku.php?id=start' target="_blank">中文ACMG</a>

           <a href='http://www.orpha.net/consor/cgi-bin/index.php' target="_blank">Orphanet</a>
           <a href='http://gnomad.broadinstitute.org/' target="_blank">GnomAD</a>
        </div>
      </nav>
    )
  }
}

Side_navbar.propTypes={

}

Side_navbar.defaultProps={

}

export default Side_navbar;
