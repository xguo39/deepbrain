import React from 'react';
import {static_files} from 'base.config';

class New_task_upload extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      father_check:false,
      father_check_pheno:false,
      mother_check:false,
      mother_check_pheno:false,
      incidental_findings_check:false,
      candidate_genes_check:false,
      input_gene_file:'尚未选择',
      input_phen:'尚未选择',
      father_gene_file:'尚未选择',
      mother_gene_file:'尚未选择',
    }
  }

  _handleSubmit(evt){
    evt.preventDefault();
    let myForm = evt.target;
    let taskData = new FormData(myForm);
    // For extracting the input checkbox element when no selected
    var inputs = document.getElementsByTagName("input");
    for(var i = 0; i < inputs.length; i++) {
        if(inputs[i].type == "checkbox" && inputs[i].checked===false) {
            taskData.append(inputs[i].name, 0);
        }
        else if(inputs[i].type == "checkbox" && inputs[i].checked){
            taskData.set(inputs[i].name, 1);
        }
    }
    for (var [key, value] of taskData.entries()) {
      console.log(key, value);
    }
    // Why can't extract the form data
    this.props.submit_task(taskData);
    myForm.reset();
    this.setState({
      father_check:false,
      father_check_pheno:false,
      mother_check:false,
      mother_check_pheno:false,
      incidental_findings_check:false,
      candidate_genes_check:false,
      input_gene_file:'尚未选择',
      input_phen:'尚未选择',
      father_gene_file:'尚未选择',
      mother_gene_file:'尚未选择',
    })
  }

  _handleChange(evt){
    let target = evt.target;
    if(target.nodeName==='INPUT'){
         switch (target.id) {
           case 'input_gene_file':
             this.setState({...this.state, input_gene_file:target.files[0].name});
             break;
           case 'input_phen':
             this.setState({...this.state, input_phen:target.files[0].name});
             break;
           case 'father_gene_file':
             this.setState({...this.state, father_gene_file:target.files[0].name});
             break;
           case 'mother_gene_file':
             this.setState({...this.state, mother_gene_file:target.files[0].name});
             break;
           default:
             break;
         }
    }
  }

  _handleClick(evt){
    let target = evt.target;
    if(target.nodeName==='LABEL'){
      switch (target.htmlFor) {
        case 'check_father':
          this.setState({...this.state, father_check:!this.state.father_check});
          break;

        case 'check_father_pheno':
          this.setState({...this.state, father_check_pheno:!this.state.father_check_pheno});
          break;

        case 'check_mother':
          this.setState({...this.state, mother_check:!this.state.mother_check});
          break;

        case 'check_mother_pheno':
          this.setState({...this.state, mother_check_pheno:!this.state.mother_check_pheno});
          break;

        case 'check_incidental_findings':
          this.setState({...this.state, incidental_findings_check:!this.state.incidental_findings_check});
          break;

        case 'check_candidate_genes':
          this.setState({...this.state, candidate_genes_check:!this.state.candidate_genes_check});
          break;

        case 'task_submit':
          console.log('submit trigger');
          break;

        default:
          break;
      }
    }
    else if (target.id === 'task_submit') {
      if(this.state.input_gene_file === '尚未选择'){
        alert('请选择基因文件');
      }
    }
    else if (target.className === 'fade-anchor'){
       let content = document.getElementById('fade-content');
       content.style["max-height"] = 'none';
       target.outerHTML='';
    }
    else if (target.id === 'format_instruction'){
       window.open(`${static_files}instruction.pdf`, "使用说明");
    }
  }

  render(){
    return (
      <div className='new_task_upload' >
        <form id="myForm"
          name="myForm"
          encType="multipart/form-data"
          onSubmit={(evt)=>this._handleSubmit(evt)}
          onClick={(evt)=>this._handleClick(evt)}>
        <div className='form-tb'>
          <div className='tb-section'>
            {/* task name */}
            <div className='tr tr-widen-sm'>
                <div className='td1'><label htmlFor='enter_task_name'>任务名称:</label></div>
                <div className='td2'><input id='enter_task_name' type="text" name="task_name" placeholder="Task name" required autoFocus={true}/></div>
                <div className='td2'><span id='format_instruction' className='highlight'>使用说明</span></div>
                {/* <div className='td2'><a href={`${static_files}使用说明.docx`} className='highlight'>使用说明</a></div> */}
            </div>
            {/* gender and age */}
            <div className='tr tr-stripe tr-widen'>
                <div className='td1 td-left'><label>性别:</label></div>
                <div className='td2'>
                  <label className="radio-inline"><input type="radio" required name="patient_gender" value='1'/>男</label>
                  <label className="radio-inline"><input type="radio" required name="patient_gender" value='2'/>女</label>
                  <label className="radio-inline"><input type="radio" required name="patient_gender" value='0'/>不明</label>
                </div>
                <div className='td2'>
                  <span style={{marginRight:'10px'}}>年龄:</span>
                  <input id='patient_age' type="text" name="patient_age" placeholder="Age" style={{width:'40px'}}/>
                </div>
            </div>
            {/* gene file */}
            <div className='tr tr-widen'>
                <div className='td1'><label>基因信息:</label></div>
                <div className='td2'>
                  <label htmlFor='input_gene_file' className='file_input'>
                    <span>选择文件</span>
                    <input id='input_gene_file'
                      type="file"
                      name="gene_file"
                      required
                      accept=".txt,.xlsx,.xls,.csv,.vcf"
                      onChange={(evt)=>this._handleChange(evt)}/>
                    <span className='prompt'>{this.state.input_gene_file}</span>
                  </label>
                </div>

                <div className='td2'><span>选择上传 VCF 文件或 filtered-VCF 文件 <br/>(.vcf .txt .xls .csv) 详细请参考使用说明</span></div>
                {/* <div className='td2'><span>选择 Vcf 文件／ .txt .xls .csv文件<br/>（文件需包含 gene 与 HGVS cDNA）</span></div> */}
            </div>
          </div>

          <p className='break-hint'>以下为选填信息</p>

          <div id='fade-content' className='fade-content' onClick={(evt)=>this._handleClick(evt)}>

            {/* Pheno info */}
            <div className='tb-section'>
              <div className='tr'>
                  <div className='td1'><label>表型信息:</label></div>
                  <div className='td2'>
                    <label htmlFor='input_phen' className='file_input'>
                      <span>选择文件</span>
                      <input
                        id='input_phen'
                        type="file"
                        name="input_phen"
                        accept=".txt"
                        onChange={(evt)=>this._handleChange(evt)}/>
                      <span className='prompt'>{this.state.input_phen}</span>
                   </label>
                  </div>
                  <div className='td2'><span>文字输入</span><br/>
                      <textarea id = "myTextArea"
                            name = "input_text_phenotype"
                            rows = "4"
                            cols = "35"
                            maxLength = "300"
                            placeholder = "表型间使用逗号分割&nbsp;(支持中英文输入)"></textarea></div>
              </div>
            </div>

            {/* Parent_info file */}
            <div className='tb-section'>
              <div className='tr'>
                  <div className='td1'>
                    <label htmlFor='parents_info'>
                      父母信息:
                    </label>
                  </div>
                  <div className='td2'>是否提供父亲基因信息:</div>
                  <div className='td2'>
                      <a data-toggle='collapse' className='switch' href='#father_detail' onClick={(evt)=>this._handleClick(evt)}>
                          <input type='checkbox'
                            id='check_father'
                            name='check_father'
                            checked={this.state.father_check}
                            onChange={(evt)=>{this._handleChange(evt)}}/>
                            <label htmlFor='check_father' className='check slider round'></label>
                      </a>
                      <span >否/是 </span>
                  </div>
              </div>
              <div id='father_detail' className='collapse'>
                <div className='tr'>
                  <div className='td1'></div>
                  <div className='td2'><span>是否与父亲有相同表型:</span></div>
                  <div className='td2'>
                    <a className='switch' onClick={(evt)=>this._handleClick(evt)}>
                        <input type='checkbox'
                          id='check_father_pheno'
                          name='check_father_pheno'
                          checked={this.state.father_check_pheno}
                          value='1'
                          onChange={(evt)=>{this._handleChange(evt)}}/>
                          <label htmlFor='check_father_pheno' className='check slider round'></label>
                    </a>
                    <span >否/是</span>
                  </div>
                </div>
                <div className='tr'>
                  <div className='td1'></div>
                  <div className='td2'><span>上传父亲基因信息:<br/><span>(若上传文件已包含父亲NGS数据则无需再单独上传)</span></span></div>
                  <div className='td2'>
                    <label htmlFor='father_gene_file' className='file_input'>
                      <span>选择文件</span>
                      <input
                        id='father_gene_file'
                        type="file"
                        name="father_gene_file"
                        accept=".txt,.xlsx,.xls,.csv,.vcf"
                        onChange={(evt)=>this._handleChange(evt)}/>
                      <span className='prompt'>{this.state.father_gene_file}</span>
                    </label>
                  </div>
                </div>
              </div>
              <div className='tr'>
                  <div className='td1'></div>
                  <div className='td2'><span>是否提供母亲基因信息:</span></div>
                  <div className='td2'>
                    <a data-toggle='collapse' className='switch' href='#mother_detail' onClick={(evt)=>this._handleClick(evt)}>
                        <input type='checkbox'
                          id='check_mother'
                          name='check_mother'
                          checked={this.state.mother_check}
                          onChange={(evt)=>{this._handleChange(evt)}}/>
                          <label htmlFor='check_mother' className='check slider round'></label>
                    </a>
                    <span>否/是</span>
                  </div>
              </div>
              <div id='mother_detail' className='collapse'>
                <div className='tr'>
                  <div className='td1'></div>
                  <div className='td2'><span>是否与母亲有相同表型:</span></div>
                  <div className='td2'>
                    <a className='switch' onClick={(evt)=>this._handleClick(evt)}>
                        <input type='checkbox'
                          id='check_mother_pheno'
                          name='check_mother_pheno'
                          checked={this.state.mother_check_pheno}
                          onChange={(evt)=>{this._handleChange(evt)}}/>
                          <label htmlFor='check_mother_pheno' className='check slider round'></label>
                    </a>
                    <span>否/是</span>
                  </div>
                </div>
                <div className='tr'>
                  <div className='td1'></div>
                  <div className='td2'><span>上传母亲基因信息:<br/><span>(若上传文件已包含母亲NGS数据则无需再单独上传)</span></span></div>
                  <div className='td2'>
                    <label htmlFor='mother_gene_file' className='file_input'>
                      <span>选择文件</span>
                      <input
                        id='mother_gene_file'
                        type="file"
                        name="mother_gene_file"
                        accept=".txt,.xlsx,.xls,.csv,.vcf"
                        onChange={(evt)=>this._handleChange(evt)}/>
                      <span className='prompt'>{this.state.mother_gene_file}</span>
                   </label>
                  </div>
                </div>
              </div>
            </div>

            {/* Report requirement */}
            <div className='tb-section'>
              <div className='tr'>
                  <div className='td1'><label htmlFor='requirement'>报告要求:</label></div>
                  <div className='td2'>
                    <span>是否要求 incidental findings
                      (<a href='http://www.nature.com/gim/journal/v19/n2/full/gim2016190a.html' target="_blank">ACMG 59个基因</a>) 报告：
                    </span>
                  </div>
                  <div className='td2'>
                    <a className='switch' onClick={(evt)=>this._handleClick(evt)}>
                        <input type='checkbox'
                          id='check_incidental_findings'
                          name='check_incidental_findings'
                          checked={this.state.incidental_findings_check}
                          onChange={(evt)=>{this._handleChange(evt)}}/>
                          <label htmlFor='check_incidental_findings' className='check slider round'></label>
                    </a>
                    <span>否/是</span>
                  </div>
              </div>
              <div className='tr'>
                  <div className='td1'></div>
                  <div className='td2'><span>是否要求 candidate genes 报告：</span></div>
                  <div className='td2'>
                    <a className='switch' onClick={(evt)=>this._handleClick(evt)}>
                        <input type='checkbox'
                          id='check_candidate_genes'
                          name='check_candidate_genes'
                          checked={this.state.candidate_genes_check}
                          onChange={(evt)=>{this._handleChange(evt)}}/>
                          <label htmlFor='check_candidate_genes' className='check slider round'></label>
                    </a>
                    <span>否/是</span>
                  </div>
              </div>
              </div>

            <div className="fade-anchor"><span className="fade-anchor-text">展示所有选填信息</span></div>
          </div>


          </div>
          <input id='task_submit' type="submit" value="提交" onClick={(evt)=>this._handleClick(evt)}/>
       </form>
      </div>

    )
  }
}

New_task_upload.propTypes={
  submit_task:React.PropTypes.func,
}

New_task_upload.defaultProps={
  submit_task:()=>{}
}

export default New_task_upload;
