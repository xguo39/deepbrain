import React from 'react';
import {
  BrowserRouter as Router,
  Route,
  Link
} from 'react-router-dom';
import Side_navbar from './Side_navbar.jsx';
import {static_image} from 'base.config';
import New_task from './New_task.jsx';
import Task_list from './Task_list.jsx';


class Main_area extends React.Component{
  constructor(props){
    super(props);
  }

  render(){
    return(
       <div className='main_area container-fluid'>
         <Router>
           <div className='row'>
             <Side_navbar />
             <main className='col-sm-10 content'>
               <Route exact path="/home/ch/" component={New_task}/>
               <Route path="/home/ch/task_list" component={Task_list}/>
               {/* <Route path="/topics" component={Feedback}/> */}
             </main>
           </div>
         </Router>
       </div>
    )
  }
}

Main_area.propTypes={

}

Main_area.defaultProps={

}

export default Main_area;
