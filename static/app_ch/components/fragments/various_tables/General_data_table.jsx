import React from 'react';
import * as Table from 'reactabular-table';
import * as sort from 'sortabular';
import orderBy from 'lodash/orderBy';
import { compose } from 'redux';
import {Paginator, paginate} from '../../helpers';
const mappingDict={
  gene:'基因',transcript:'转录本',variant:'c.DNA',protein:'蛋白质',zygosity:'配型',correlated_phenotypes:'表型匹配',
  pheno_match_score:'表型匹配得分', hit_criteria:'ACMG评判标准', pathogenicity:'致病性', criteria:'标准',
  interpretation:'解读', pathogenicity_score:'致病性得分', final_score:'总分'
}

class General_data_table extends React.Component{
  constructor(props){
    super(props);
    // Define the transforms of rows
    const getSortingColumns = () => this.state.sortingColumns || {};
    const sortingOrder = {
      FIRST: 'asc',
      asc: 'desc',
      desc: 'asc'
    };
    const sortable = sort.sort({
      getSortingColumns,
      onSort: selectedColumn => {
        this.setState({
          sortingColumns: sort.byColumn({ // sort.byColumn would work too
            sortingColumns: this.state.sortingColumns,
            selectedColumn,
            sortingOrder
          })
        });
      },
      strategy: sort.strategies.byProperty  // Use property strategy over index one given we have nested data
    });
    // Dynamically generate the columns
    let columns = [];
    let sortingColumns={};
    let order = 0;
    for(let column_key in this.props.table_data[0]){
      if(typeof this.props.table_data[0][column_key] === "number"){
        sortingColumns[column_key]={
          direction:'desc',
          position:order
        }
        order++
        columns.push({
          property:`${column_key}`,
          header:{
            label:`${mappingDict[column_key]?mappingDict[column_key]:column_key}`,
            transforms:[sortable],
            formatters:[
              sort.header({
                getSortingColumns,
              })
           ],
          }
        })
      }else{
        columns.push({
          property:`${column_key}`,
          header:{
            label:`${mappingDict[column_key]?mappingDict[column_key]:column_key}`
          }
        })
      }
    }
    this.state={
      sortingColumns:sortingColumns,
      columns: columns,
      rows:this.props.table_data,
      pagination: { // initial pagination settings
       page: 1,
       perPage: 10
     }
    };
    this._handleSelect = this._handleSelect.bind(this);
  }

  componentWillReceiveProps(props){
    // Define the transforms of rows
    const getSortingColumns = () => this.state.sortingColumns || {};
    const sortingOrder = {
      FIRST: 'asc',
      asc: 'desc',
      desc: 'asc'
    };
    const sortable = sort.sort({
      getSortingColumns,
      onSort: selectedColumn => {
        this.setState({
          sortingColumns: sort.byColumn({ // sort.byColumn would work too
            sortingColumns: this.state.sortingColumns,
            selectedColumn,
            sortingOrder
          })
        });
      },
      strategy: sort.strategies.byProperty  // Use property strategy over index one given we have nested data
    });
    // Dynamically update the columns and rows
    let columns = [];
    let sortingColumns={};
    let order = 0;
    for(let column_key in props.table_data[0]){
      if(typeof props.table_data[0][column_key] === "number"){
        sortingColumns[column_key]={
          direction:'desc',
          position:order
        }
        order++
        columns.push({
          property:`${column_key}`,
          header:{
            label:`${mappingDict[column_key]?mappingDict[column_key]:column_key}`,
            transforms:[sortable],
            formatters:[
              sort.header({
                getSortingColumns,
              })
           ],
          }
        })
      }else{
        columns.push({
          property:`${column_key}`,
          header:{
            label:`${mappingDict[column_key]?mappingDict[column_key]:column_key}`
          }
        })
      }
    }
    this.setState({
      sortingColumns:sortingColumns,
      columns: columns,
      rows: props.table_data,
      pagination: { // initial pagination settings
       page: 1,
       perPage: 10
     }
    })
  }

  _handleBodyRow(row, { rowIndex, rowKey }){
    let className='clickable';
    return {
      className:className
    }
  }

  // hanle pagination select
  _handleSelect(page){
    const pages = Math.ceil(
      this.state.rows.length / this.state.pagination.perPage
    );
    this.setState({
     pagination: {
       ...this.state.pagination,
       page: Math.min(Math.max(page, 1), pages)
     }
   });
  }

  render(){
    const{columns, rows, sortingColumns, pagination} = this.state;
    const paginated = compose(
      paginate(pagination),
      sort.sorter({
        columns: columns,
        sortingColumns,
        sort: orderBy,
        strategy: sort.strategies.byProperty
      })
    )(rows);
    return(
      <div className='general_data_table'>
        <div>
          <Table.Provider
            className='pure-table table-striped'
            columns={columns}>

              <Table.Header />

              <Table.Body
                rows={paginated.rows}
                rowKey={({ rowData, rowIndex }) => rowIndex}
                onRow={(row, { rowIndex, rowKey })=>this._handleBodyRow(row, { rowIndex, rowKey })}/>

            </Table.Provider>

            <div className="controls">
             <Paginator
               pagination={pagination}
               pages={paginated.amount}
               onSelect={this._handleSelect}
             />
           </div>
        </div>
      </div>
    )
  }
}

General_data_table.propTypes={
  getSortingColumns:React.PropTypes.func
}

General_data_table.defaultProps={
  getSortingColumns:()=>{}
}

export default General_data_table;
