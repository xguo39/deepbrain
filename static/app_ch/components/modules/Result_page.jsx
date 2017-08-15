import React from 'react';
import {static_image} from 'base.config';
import {
  General_data_table, Annotation_page
} from 'components/fragments';

class Result_page extends React.Component{
  constructor(props){
    super(props);
    this.state={
      // current_table:<Summary_table table_data={this.props.summary_table_data}/>,
      current_data:this.props.summary_table_data
    }
  }

  componentWillMount(){
    console.log(this.props.match.params);
    const task_id = this.props.match.params.task_id;
    const task_name = this.props.match.params.task_name;
    this.props.fetchResultData()
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
      //let liIndex = Array.prototype.indexOf.call(children, target);
      for(let li of children){
        li.classList.remove('active');
      }
      target.classList.add('active');
      switch (target.getAttribute('alt')) {
        case 'summary_table':
          // Waited: Here we cut off the correlated_phenotypes:'biaoxingpipei',
          this.setState({
            ...this.state,
            current_data:this.props.summary_table_data,
          })
          break;

        case 'phenotype_match_table':
          // Waited: Here we cut off the summary_table_data to phenotype_match_table
          this.setState({
            ...this.state,
            current_data:this.props.phenotype_match_table,
          })
          break;

        case 'incidental_finding_table':
          this.setState({
            ...this.state,
            current_data:this.props.incidental_table_data,
          })
          break;

        case 'candidate_gene_table':
          this.setState({
            ...this.state,
            current_data:this.props.candidate_table_data,
          })
          break;

        case 'input_gene_table':
          this.setState({
            ...this.state,
            current_data:this.props.input_table_data,
          })
          break;

        default:
          break;
      }
    }

    // Click to check the detail annotation of a gene variant
    if(target.nodeName==='TD'){
      let gene = target.parentElement.children[0].innerHTML;
      let transicript = target.parentElement.children[1].innerHTML;
      let current_path = this.props.match.url;
      this.props.showAnnotation(current_path, gene, transicript);
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
             {/* {this.state.current_table} */}
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

  summary_table_data:React.PropTypes.array,
  incidental_table_data:React.PropTypes.array,
  candidate_table_data:React.PropTypes.array,
  input_table_data:React.PropTypes.array
}

Result_page.defaultProps={
  goBack:()=>{},
  showAnnotation:()=>{},
  summary_table_data:[
     {
       gene:'WWOX',
       transcript:'chr16:g.78466583C>G',
       variant:'GCGTG',
       protein:'danbaizhi',
       zygosity:'peixing',
       correlated_phenotypes:'biaoxingpipei',
       pheno_match_score:39,
       hit_criteria:"PM2|BP4",
       pathogenicity:'Uncertain Significance',
       pathogenicity_score:0.88,
       final_score:1.8
     },
     {
       gene:'WNT7A',
       transcript:'chr3:g.13896304C>T',
       variant:'GCGTG',
       protein:'danbaizhi',
       zygosity:'peixing',
       correlated_phenotypes:'biaoxingpipei',
       pheno_match_score:45,
       hit_criteria:"PM2|BP4",
       pathogenicity:'Uncertain Significance',
       pathogenicity_score:1.28,
       final_score:1.1
     }
  ],
  phenotype_match_table:[
    {
      gene:'WWOX',
      transcript:'chr16:g.78466583C>G',
      variant:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      correlated_phenotypes:'biaoxingpipei',
      pheno_match_score:39,
    },
    {
      gene:'WNT7A',
      transcript:'chr3:g.13896304C>T',
      variant:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      correlated_phenotypes:'biaoxingpipei',
      pheno_match_score:45,
    }
  ],
  incidental_table_data:[
    {
      gene:'WWOX',
      transcript:'chr16:g.78466583C>G',
      variant:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      pheno_match_score:39,
      hit_criteria:"PM2|BP4",
      pathogenicity:'Uncertain Significance',
    },
    {
      gene:'Shio OM4',
      transcript:'chr16:g.78466583C>G',
      variant:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      pheno_match_score:88,
      hit_criteria:"PM2|BP4",
      pathogenicity:'Uncertain Significance',
    }
  ],
  candidate_table_data:[
    {
      gene:'WWOX',
      transcript:'chr16:g.78466583C>G',
      cDNA:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      correlated_phenotypes:'from paper'
    },
    {
      gene:'Shio OM4',
      transcript:'chr16:g.78466583C>G',
      cDNA:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      correlated_phenotypes:'from paper'
    }
  ],
  input_table_data:[
    {
      gene:'WWOX',
      transcript:'chr16:g.78466583C>G',
      cDNA:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      pheno_matched_score:25,
    },
    {
      gene:'Shio OM4',
      transcript:'chr16:g.78466583C>G',
      cDNA:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      pheno_matched_score:39,
    }
  ]
}

export default Result_page;
