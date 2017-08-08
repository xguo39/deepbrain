import React from 'react';
import {static_image} from 'base.config.js';
import Summary_table from 'components/fragments/Summary_table.jsx';

class Result_page extends React.Component{
  constructor(props){
    super(props);
    this.state={
      current_table:
        <Summary_table table_data={this.props.summary_table_data}/>,
      active_nav:0
    }
  }

  _handleClick(evt){
    let target = evt.target;
    if(target.alt === 'back-sign'){
      this.props.goBack();
    }
    // When click on the table row
    if(target.nodeName==='TD'){
      console.log(target.parentElement.firstChild.innerHTML);
    }
  }

  _handleSubmit(evt){
    evt.preventDefault();
    let review_form_data = new FormData(evt.target);
  }

  render(){
    return(
      <div className='result_page'>
         <div className='back-sign' onClick={(evt)=>this._handleClick(evt)}>
            <img src={static_image+'back.png'} alt='back-sign'></img>
            <span>返回</span></div>
         {/* Result table navigation */}
         <div className='result_table_nav' role="navigation" >
            <ul className='' onClick={(evt)=>this._handleClick(evt)}>
              <li className='active'>
                <span>总表</span>
              </li>
              <li className=''>
                <span>表型对应表</span>
              </li>
              <li className=''>
                <span>附带发现表</span>
              </li>
              <li className=''>
                <span>备选基因表</span>
              </li>
              <li className=''>
                <span>输入基因</span>
              </li>
              <li className=''>
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
           {/* Main Result Area */}
           <div className='result_table' onClick={(evt)=>this._handleClick(evt)}>
             {this.state.current_table}
           </div>
         </div>
      </div>
    )
  }
}

Result_page.propTypes={
  goBack:React.PropTypes.func.isRequired,
  result_table_data:React.PropTypes.array
}

Result_page.defaultProps={
  goBack:()=>{},
  summary_table_data:[
     {
       gene:'WWOX',
       transcript:'chr16:g.78466583C>G',
       cDNA:'GCGTG',
       protein:'danbaizhi',
       zygosity:'peixing',
       pheno_matched_score:39,
       ACMG_criteria_matched:"PM2|BP4",
       clinical_significance:'Uncertain Significance',
       clinical_significance_score:55,
       classification_score:0.88,
       total_score:1.8
     },
     {
       gene:'WNT7A',
       transcript:'chr3:g.13896304C>T',
       cDNA:'GCGTG',
       protein:'danbaizhi',
       zygosity:'peixing',
       pheno_matched_score:45,
       ACMG_criteria_matched:"PM2|BP4",
       clinical_significance:'Uncertain Significance',
       clinical_significance_score:33,
       classification_score:1.28,
       total_score:1.1
     }
  ]
}

export default Result_page;
