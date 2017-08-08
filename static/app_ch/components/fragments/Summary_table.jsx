import React from 'react';
import * as Table from 'reactabular-table';


class Summary_table extends React.Component{
  constructor(props){
    super(props);
    this.state={
      columns:[
         {
           property:'gene',
           header:{
             label:'基因'
           }
         },
         {
           property:'transcript',
           header:{
             label:'转录本'
           }
         },
         {
           property:'cDNA',
           header:{
             label:'cDNA'
           }
         },
         {
           property:'protein',
           header:{
             label:'蛋白质'
           }
         },
         {
           property:'zygosity',
           header:{
             label:'配型'
           }
         },
         {
           property:'pheno_matched_score',
           header:{
             label:'表型匹配得分'
           }
         },
         {
           property:'ACMG_criteria_matched',
           header:{
             label:'ACMG评判标准'
           }
         },
         {
           property:'clinical_significance',
           header:{
             label:'致病性'
           }
         },
         {
           property:'clinical_significance_score',
           header:{
             label:'致病性得分'
           }
         },
         {
           property:'classification_score',
           header:{
             label:'致病性得分'
           }
         },
         {
           property:'total_score',
           header:{
             label:'总分'
           }
         }
      ],
      rows:this.props.table_data
    };
  }

  _handleBodyRow(row, { rowIndex, rowKey }){
    let className='clickable';
    return {
      className:className
    }
  }

  render(){
    const{columns, rows} = this.state;
    return (
      <div className='summary_table'>
        <div>
          <Table.Provider
            className='pure-table '
            columns={columns}>

              <Table.Header />

              <Table.Body
                rows={rows}
                rowKey='gene'
                onRow={(row, { rowIndex, rowKey })=>this._handleBodyRow(row, { rowIndex, rowKey })}/>

            </Table.Provider>
        </div>
      </div>
    )
  }
}

Summary_table.propTypes={

}

Summary_table.defaultProps={

}

export default Summary_table;
