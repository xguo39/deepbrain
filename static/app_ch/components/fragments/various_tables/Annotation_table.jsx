import React from 'react';
import * as Table from 'reactabular-table';

class Annotation_table extends React.Component{
  constructor(props){
    super(props);
    this.state={
      columns:[
        {
          property:'standard',
          header:{
            label:'标准'
          },
          props:{
            className:'col1'
          }
        },
        {
          property:'analyze',
          header:{
            label:'解读'
          },
          props:{
            className:'col2'
          }
        }
      ],
      rows:this.props.table_data
    }
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
              rowKey='standard'
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
