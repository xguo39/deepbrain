import React from 'react';


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
    let formData = new FormData(evt.target);
    // alert('hahah submit yo!');
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

        default:
          break;
      }
    };
  }

  render(){
    return (
      <div className='new_task_upload'>
        <form id="myForm" name="myForm" encType="multipart/form-data" onSubmit={(evt)=>this._handleSubmit(evt)}>
        <div className='form-tb'>

          <div className='tb-section'>
            <div className='tr'>
                <div className='td1'><label htmlFor='enter_task_name'>任务名称:</label></div>
                <div className='td2'><input id='enter_task_name' type="text" name="task_name" placeholder="Active" required autoFocus={true}/></div>
                <div className='td2'><span>使用说明</span></div>
            </div>
            <div className='tr tr-stripe'>
                <div className='td1'><label>基因信息:</label></div>
                <div className='td2'>
                  <label htmlFor='input_gene_file' className='file_input'>
                    <span>选择文件</span>
                    <input id='input_gene_file'
                      type="file"
                      name="gene_file"
                      required accept=".txt,.xlsx,.xls,.csv,.vcf"
                      onChange={(evt)=>this._handleChange(evt)}/>
                    <span className='prompt'>{this.state.input_gene_file}</span>
                  </label>
                </div>
                <div className='td2'><span>选择 Vcf 文件／ .txt .xls .csv文件<br/>（文件需包含 gene 与 HGVS cDNA）</span></div>
            </div>
            <div className='tr'>
                <div className='td1'><label>表型信息:<br/>（可选）</label></div>
                <div className='td2'>
                  <label htmlFor='input_phen' className='file_input'>
                    <span>选择文件</span>
                    <input
                      id='input_phen'
                      type="file"
                      name="symptom_file"
                      accept=".txt"
                      onChange={(evt)=>this._handleChange(evt)}/>
                    <span className='prompt'>{this.state.input_phen}</span>
                 </label>
                </div>
                <div className='td2'><span>文字输入</span><br/>
                    <textarea id = "myTextArea"
                          name = "input_text_phenotype"
                          rows = "5"
                          cols = "35"
                          maxLength = "300"
                          placeholder = "表型间使用逗号分割&nbsp;(支持中英文输入)"></textarea></div>
            </div>
          </div>

          <div className='tb-section'>
            <div className='tr'>
                <div className='td1'><label htmlFor='parents_info'>父母信息:</label></div>
                <div className='td2'><span>是否提供父亲基因信息:</span></div>
                <div className='td2'>
                    <a data-toggle='collapse' className='switch' href='#father_detail' onClick={(evt)=>this._handleClick(evt)}>
                        <input type='checkbox'
                          id='check_father'
                          name='father_check'
                          checked={this.state.father_check}
                          onChange={(evt)=>{this._handleChange(evt)}}/>
                          <label htmlFor='check_father' className='check slider round'></label>
                    </a>
                    <span >否/是</span>
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
                        name='father_check_pheno'
                        checked={this.state.father_check_pheno}
                        onChange={(evt)=>{this._handleChange(evt)}}/>
                        <label htmlFor='check_father_pheno' className='check slider round'></label>
                  </a>
                  <span >否/是</span>
                </div>
              </div>
              <div className='tr'>
                <div className='td1'></div>
                <div className='td2'><span>上传父亲基因信息:</span></div>
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
                        name='mother_check'
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
                        name='mother_check_pheno'
                        checked={this.state.mother_check_pheno}
                        onChange={(evt)=>{this._handleChange(evt)}}/>
                        <label htmlFor='check_mother_pheno' className='check slider round'></label>
                  </a>
                  <span>否/是</span>
                </div>
              </div>
              <div className='tr'>
                <div className='td1'></div>
                <div className='td2'><span>上传母亲基因信息:</span></div>
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

          <div className='tb-section'>
            <div className='tr'>
                <div className='td1'><label htmlFor='requirement'>报告要求:</label></div>
                <div className='td2'><span>是否要求 incidental findings 报告：</span></div>
                <div className='td2'>
                  <a className='switch' onClick={(evt)=>this._handleClick(evt)}>
                      <input type='checkbox'
                        id='check_incidental_findings'
                        name='incidental_findings_check'
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
                        name='candidate_genes_check'
                        checked={this.state.candidate_genes_check}
                        onChange={(evt)=>{this._handleChange(evt)}}/>
                        <label htmlFor='check_candidate_genes' className='check slider round'></label>
                  </a>
                  <span>否/是</span>
                </div>
            </div>
            </div>


          </div>
          <input id='task_submit' type="submit" value="提交" onClick={(evt)=>this._handleClick(evt)}/>
       </form>
      </div>

    )
  }
}

New_task_upload.propTypes={

}

New_task_upload.defaultProps={

}

export default New_task_upload;
