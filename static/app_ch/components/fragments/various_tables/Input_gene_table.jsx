import React from 'react';
import * as Table from 'reactabular-table';
import * as sort from 'sortabular';
import orderBy from 'lodash/orderBy';
import { compose } from 'redux';
import {Paginator, paginate} from '../../helpers';
const mappingDict={
  gene:'基因',transcript:'转录本',cDNA:'cDNA',protein:'蛋白质',zygosity:'配型',phenotype_matched:'表型匹配',
  pheno_matched_score:'表型匹配得分', ACMG_criteria_matched:'ACMG评判标准',clinical_significance:'致病性',
  classification_score:'致病性得分', total_score:'总分'
}

class Input_gene_table extends React.Component{
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
            label:`${mappingDict[column_key]}`,
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
            label:`${mappingDict[column_key]}`
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
            label:`${mappingDict[column_key]}`,
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
            label:`${mappingDict[column_key]}`
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

  _handleSelect(page){ // hanle pagination select
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
      <div className='input_gene_table'>
        <div>
          <Table.Provider
            className='pure-table table-striped'
            columns={columns}>

              <Table.Header />

              <Table.Body
                rows={paginated.rows}
                rowKey='gene'
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

Input_gene_table.propTypes={
  getSortingColumns:React.PropTypes.func
}

Input_gene_table.defaultProps={
  getSortingColumns:()=>{}
}

export default Input_gene_table;
