import React from 'react';
import * as Table from 'reactabular-table';
import {compose} from 'redux';
import * as search from 'searchtabular';

class Task_list extends React.Component{
  constructor(props){
    super(props);

    this.state={
      searchColumn: 'all',
      query: {},
      columns:[
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
            label:'提交时间'
          },
          props:{
            className:'tc2'
          }
        },
        {
          property:'status',
          header:{
            label:'状态'
          },
          cell:{
            formatters:[
              status => status?'成功':'失败'
            ]
          },
          props:{
            className:'tc1'
          },
        }
      ],
      rows:[
        {
          id:1,
          name:'xiaonan',
          time:'July 18, 2017, 12:03 p.m.',
          status:true,
          checked:true,
        },
        {
          id:2,
          name:'tianqi',
          time:'July 18, 2017, 11:03 p.m.',
          status:false,
          checked:false
        }
      ],
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
    const { searchColumn, columns, rows, query } = this.state;
    const searchedRows = compose(
      search.multipleColumns({
       columns: columns,
       query
     }),
   )(rows);
    return(
      <div className='task_list'>
        <div className='search_container'>
          <search.Field
             column={searchColumn}
             query={query}
             columns={columns}
             rows={rows}
             onColumnChange={searchColumn => this.setState({ searchColumn })}
             onChange={query => this.setState({ query })}
             components={
               {
                 props:{
                   filter:{
                     placeholder:'Search'
                   }
                 }
               }
             }
          />
        </div>
        <div className='task_list_table'>
            <Table.Provider
              className='pure-table table-striped'
              columns={columns}>

                <Table.Header />

                <Table.Body
                  rows={searchedRows}
                  rowKey='name'
                  onRow={(row, { rowIndex, rowKey })=>this._handleBodyRow(row, { rowIndex, rowKey })}/>

              </Table.Provider>
        </div>
        <p>全部共 {this.state.rows.length} 项</p>
      </div>
    )
  }
}

Task_list.propTypes={
  toResult:React.PropTypes.func.isRequired,
}

Task_list.defaultProps={
  toResult:()=>{}
}

export default Task_list;
