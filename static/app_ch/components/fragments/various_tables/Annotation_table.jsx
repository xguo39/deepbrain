import React from 'react';
import * as Table from 'reactabular-table';
// const mappingDict = {
//   criteria:'标准',
//   interpretation:'解读'
// }

class Annotation_table extends React.Component{
  constructor(props){
    super(props);
    this.state={
      columns:[
        {
          property:'criteria',
          header:{
            label:'标准'
          },
          props:{
            className:'col1'
          }
        },
        {
          property:'interpretation',
          header:{
            label:'解读'
          },
          cell:{
            formatters:[
              interpretation => this._unescapeHTML(interpretation)
            ]
          },
          props:{
            className:'col2'
          }
        }
      ],
      rows:this.props.table_data
    }
  }

  componentWillReceiveProps(props){
    console.log(props);
    this.setState({
      columns:[
        {
          property:'criteria',
          header:{
            label:'标准'
          },
          props:{
            className:'col1'
          }
        },
        {
          property:'interpretation',
          header:{
            label:'解读'
          },
          cell:{
            formatters:[
              interpretation => this._unescapeHTML(interpretation)
            ]
          },
          props:{
            className:'col2'
          }
        }
      ],
      rows:props.table_data
    })
  }

  _unescapeHTML(html) {
    var escapeEl = document.createElement('textarea');
    escapeEl.innerHTML = html;
    return  <div className='interpretation_content' dangerouslySetInnerHTML={{ __html: `${html}` }}></div>
  }

  render(){
    const {columns, rows} = this.state;
    return(
      <div className='annotation_table'>
        <Table.Provider
          className='pure-table table-striped'
          columns={columns}>
            <Table.Header />
            <Table.Body
              rows={rows}
              rowKey={({ rowData, rowIndex }) => rowIndex}
            />
          </Table.Provider>
      </div>
    )
  }
}

Annotation_table.propTypes={

}

Annotation_table.defaultProps={

}

export default Annotation_table;
