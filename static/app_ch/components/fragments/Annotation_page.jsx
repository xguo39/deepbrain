import React from 'react';
import {static_image} from 'base.config';
import {Annotation_table} from './';

class Annotation_page extends React.Component{
  constructor(props){
    super(props);
  }

  componentWillMount(){
    const gene_name = this.props.match.params.gene_name;
    const cDNA = this.props.match.params.cDNA;
    this.props.fetchAnnotation(gene_name, cDNA);
  }

  _handleClick(evt){
    let target = evt.target;
    // console.log(target);
    if(target.getAttribute('alt')==='back-sign'){
      this.props.goBack();
    }
  }

  render(){
    const gene_name = this.props.match.params.gene_name;
    const cDNA = this.props.match.params.cDNA;
    return(
      <div className='annotation_page' onClick={(evt)=>{this._handleClick(evt)}}>
         <div className='annotation_area container-fluid'>
           <div className='annotation_header'>
              <p>基因：<span>{`${gene_name}`}</span></p>
              <p>cDNA：<span>{`${cDNA}`}</span></p>
           </div>
           <img src={static_image+'cancel_icon.png'} alt='back-sign'></img>
           <Annotation_table table_data={this.props.annotation_data}/>
         </div>
      </div>
    )
  }
}

Annotation_page.propTypes={
  goBack:React.PropTypes.func,
  fetchAnnotation:React.PropTypes.func,
  annotation_data:React.PropTypes.array
}

Annotation_page.defaultProps={
  goBack:()=>{},
  annotation_data:[
    {
      standard:'变异注释',
      analyze:'xxooxoxoxoxoxoodfdsfdsfdsfdsfdfdsf'
    },
    {
      standard:'PVS1',
      analyze:'yykkdfdfsdfdsfsdfdsfsdfsdfsdfjfjdsfdksnflkndf'
    }

  ]
}

export default Annotation_page;
