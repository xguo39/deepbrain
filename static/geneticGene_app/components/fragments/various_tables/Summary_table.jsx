import React from 'react';
import * as Table from 'reactabular-table';
import * as sort from 'sortabular';
import orderBy from 'lodash/orderBy';
import { compose } from 'redux';
import {Paginator, paginate} from '../../helpers';


class Summary_table extends React.Component{
  constructor(props){
    super(props);
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
    this.state={
      sortingColumns: {
         'pheno_matched_score': {
           direction: 'desc',
           position: 2
         },
         'classification_score':{
           direction:'desc',
           position:1
         },
         'total_score':{
           direction:'desc',
           position:0
         }
       },
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
             label:'表型匹配得分',
             transforms: [sortable],
             formatters: [
               sort.header({
                 getSortingColumns,
               }),

             ]
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
           property:'classification_score',
           header:{
             label:'致病性得分',
             transforms:[sortable],
             formatters:[
               sort.header({
                 getSortingColumns,
               })
             ]
           }
         },
         {
           property:'total_score',
           header:{
             label:'总分',
             transforms:[sortable],
             formatters:[
               sort.header({
                 getSortingColumns,
               })
            ]
           }
         }
      ],
      rows:this.props.table_data,
      pagination: { // initial pagination settings
       page: 1,
       perPage: 10
     }
    };
    this._handleSelect = this._handleSelect.bind(this);
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
    // Generate paginated rows
    const paginated = compose(
      paginate(pagination),
      sort.sorter({
        columns: columns,
        sortingColumns,
        sort: orderBy,
        strategy: sort.strategies.byProperty
      })
    )(rows);
    return (
      <div className='summary_table'>
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

Summary_table.propTypes={

}

Summary_table.defaultProps={

}

export default Summary_table;
