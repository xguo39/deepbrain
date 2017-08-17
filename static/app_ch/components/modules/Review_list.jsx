import React from 'react';
import * as Table from 'reactabular-table';


class Review_list extends React.Component{
  constructor(props){
    super(props);
    this.state={
      columns:[
        {
          property:'status',
          props:{
            className:'tc1'
          },
          cell:{
            formatters:[
              status => '未评估'
            ]
          }
        },
        {
          property:'name',
          header:{
            label:'名称'
          },
          props:{
            className:'tc1'
          }
        },
        {
          property:'time',
          header:{
            label:'提交时间',
          },
          props:{
            className:'tc2'
          }
        }
      ],
      rows:[
        // {
        //   id:1,
        //   name:"xiaonan",
        //   time:'July 18, 2017, 12:03 p.m.',
        //   status:false
        // },
        // {
        //   id:2,
        //   name:"tianqi",
        //   time:'July 18, 2017, 12:03 p.m.',
        //   status:false
        // }
      ]
    }
  }

  _handleBodyRow(row, { rowIndex, rowKey }){
    let className = 'clickable';
    return {
      onClick:()=>{
        this.props.toResult(row.id, row.name);
      },
      className:className,
    }
  }

  render(){
    const {columns, rows} = this.state;
    return(
      <div className='review_list'>
         <div className='review_list_table'>
           <Table.Provider
             className='pure-table table-striped'
             columns={columns}>

               <Table.Header />

               <Table.Body
                 rows={rows}
                 rowKey={({ rowData, rowIndex }) => rowIndex}
                 onRow={(row, { rowIndex, rowKey })=>this._handleBodyRow(row, { rowIndex, rowKey })}/>

             </Table.Provider>
         </div>
         <p>全部共 {this.state.rows.length} 项</p>
      </div>
    )
  }
}

Review_list.propTypes={
  toResult:React.PropTypes.func.isRequired,
}

Review_list.defaultProps={
  toResult:()=>{}
}

export default Review_list;
