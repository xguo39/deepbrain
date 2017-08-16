import React from 'react';
import {static_image} from 'base.config';
import {
  General_data_table, Annotation_page
} from 'components/fragments';

class Result_page extends React.Component{
  constructor(props){
    super(props);
    let summary_data = [...this.props.result_data.summary_table_data];
    summary_data[0] = {...this.props.result_data.summary_table_data[0]};
    delete summary_data[0]['correlated_phenotypes'];
    delete summary_data[0]['id'];
    this.state={
      current_table:'summary_table',
      current_data:summary_data
    }
  }

  componentWillMount(){
    const task_id = this.props.match.params.task_id;
    this.props.fetchResultData(task_id);
  }

  _handleClick(evt){
    let target = evt.target;
    let parentTarget = evt.currentTarget;
    // Click to return to former page
    if(target.alt === 'back-sign'){
      this.props.goBack();
    }
    // Click to select diffrerent table_data
    if(parentTarget.id === 'result_table_nav_list'){
      let children = parentTarget.children;
      for(let li of children){
        li.classList.remove('active');
      }
      target.classList.add('active');
      switch (target.getAttribute('alt')) {
        case 'summary_table':
          // Waited: Here we cut off the correlated_phenotypes:'biaoxingpipei',
          let summary_data = [...this.props.result_data.summary_table_data];
          summary_data[0] = {...this.props.result_data.summary_table_data[0]};
          delete summary_data[0]['correlated_phenotypes'];
          delete summary_data[0]['id'];
          // delete this.props.result_data.summary_table_data[0]['correlated_phenotypes'];
          this.setState({
            ...this.state,
            current_data:summary_data,
          })
          break;

        case 'phenotype_match_table':
          // Waited: Here we cut off the summary_table_data to phenotype_match_table
          let phenotype_match_data = [...this.props.result_data.summary_table_data];
          phenotype_match_data[0] = {...this.props.result_data.summary_table_data[0]};
          delete phenotype_match_data[0]['hit_criteria'];delete phenotype_match_data[0]['pathogenicity'];
          delete phenotype_match_data[0]['pathogenicity_score'];delete phenotype_match_data[0]['final_score'];
          delete phenotype_match_data[0]['id'];
          this.setState({
            ...this.state,
            current_data:phenotype_match_data,
          })
          break;

        case 'incidental_finding_table':
          this.setState({
            ...this.state,
            current_data:this.props.result_data.incidental_table_data,
          })
          break;

        case 'candidate_gene_table':
          this.setState({
            ...this.state,
            current_data:this.props.result_data.candidate_table_data,
          })
          break;

        case 'input_gene_table':
          this.setState({
            ...this.state,
            current_data:this.props.result_data.input_gene_data,
          })
          break;

        case 'generate_result_table':
          this.setState({
            ...this.state,
            current_data:this.props.result_data.interpretation_data,
          })
          break;

        default:
          break;
      }
    }

    // Click to check the detail annotation of a gene variant
    if(target.nodeName==='TD'){
      let gene = target.parentElement.children[0].innerHTML;
      let transcript = target.parentElement.children[1].innerHTML;
      let current_path = this.props.match.url;
      this.props.showAnnotation(current_path, gene, transcript);
    }
    //
  }

  _handleSubmit(evt){
    evt.preventDefault();
    let review_form_data = new FormData(evt.target);
  }

  render(){
    return(
      <div className='result_page'>
         {/* Backsign area */}
         <div className='back-sign' onClick={(evt)=>this._handleClick(evt)}>
            <img src={static_image+'back.png'} alt='back-sign'></img>
            <span>返回 | {`${this.props.match.params.task_name}`}</span>
          </div>
         {/* Result table navigation */}
         <div className='result_table_nav' role="navigation" >
            <ul id='result_table_nav_list' onClick={(evt)=>this._handleClick(evt)}>
              <li className='active' alt='summary_table'>
                <span>总表</span>
              </li>
              <li className='' alt='phenotype_match_table'>
                <span>表型对应表</span>
              </li>
              <li className='' alt='incidental_finding_table'>
                <span>附带发现表</span>
              </li>
              <li className='' alt='candidate_gene_table'>
                <span>备选基因表</span>
              </li>
              <li className='' alt='input_gene_table'>
                <span>输入基因</span>
              </li>
              <li className='' alt='generate_result_table'>
                <span>生成报表</span>
              </li>
            </ul>
            <button
              id='review_button'
              className='btn btn-primary btn-xs'
              data-toggle="collapse"
              data-target='#review_block'
              onClick={(evt)=>this._handleClick(evt)}>
              结果评估
            </button>
         </div>
         {/* Main result area */}
         <div className='result_area'>
           {/* Result review form */}
           <div id='review_block' className="collapse review_block">
             <form id="reviewForm"
               name="review_form"
               className='question_container'
               encType="multipart/form-data"
               onSubmit={(evt)=>this._handleSubmit(evt)}>
              <div className='review_question q1'>
                <p>1. 您的分子诊断结果是什么?</p>
                <textarea
                  name = "q1"
                  rows = "2"
                  cols = "20"
                  maxLength = "300"
                  placeholder = "Text">
                </textarea>
              </div>
              <div className='review_question q2'>
                <p>2. 表型匹配是否符合您的预期?<br/>(是否在第一页)</p>
                <label><input type="radio" name="q2" value='true'/><span>是</span></label>
                <label><input type="radio" name="q2" value='false'/><span>否</span></label>
                <br/>
                <input
                  id='review_submit'
                  className='btn btn-primary'
                  type="submit"
                  value='提交'
                  onClick={(evt)=>this._handleClick(evt)}/>
              </div>
              <div className='review_question q3'>
                <p>3. 致病性判断是否符合您的预期?<br/> &nbsp;</p>
                <label><input type="radio" name="q3" value='true'/><span>是</span></label>
                <label><input type="radio" name="q3" value='false'/><span>否</span></label>
                <br/>

              </div>
            </form>
           </div>
           {/* Table Area */}
           <div className='result_table' onClick={(evt)=>this._handleClick(evt)}>
             <General_data_table table_data={this.state.current_data}/>
           </div>
         </div>
      </div>
    )
  }
}

Result_page.propTypes={
  goBack:React.PropTypes.func.isRequired,
  showAnnotation:React.PropTypes.func,
  fetchResultData:React.PropTypes.func,
  result_data:React.PropTypes.object,
}

Result_page.defaultProps={

}

export default Result_page;
