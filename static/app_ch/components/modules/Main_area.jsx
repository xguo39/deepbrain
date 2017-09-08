import React from 'react';
import {
  Route,
  Link
} from 'react-router-dom';

import Side_navbar from 'containers/modules/Side_navbar_container';
import {static_image} from 'base.config';
import New_task from 'containers/modules/New_task_container';
// import Task_list from './Task_list.jsx';
import Task_list from 'containers/modules/Task_list_container';
import Review_list from 'containers/modules/Review_list_container';
import Result_page from 'containers/modules/Result_page_container';
import Annotation_page from 'containers/fragments/Annotation_page_container';


class Main_area extends React.Component{
  constructor(props){
    super(props);
  }

  render(){
    return(
       <div className='main_area container-fluid'>
             <div className='row'>
               <Route path='/' component={Side_navbar}/>
               <main className='col-sm-10 content'>
                 <Route exact path="/home/ch" component={New_task}/>
                 <Route path="/home/ch/task_list" component={Task_list}/>
                 <Route path="/home/ch/review_list" component={Review_list}/>
                 <Route path="/home/ch/result/:task_id/:task_name" component={Result_page}/>
                 <Route path="/home/ch/result/:task_id/:task_name/:gene_name" component={Annotation_page}/>
               </main>
             </div>
       </div>
    )
  }
}

Main_area.propTypes={

}

Main_area.defaultProps={

}

export default Main_area;
