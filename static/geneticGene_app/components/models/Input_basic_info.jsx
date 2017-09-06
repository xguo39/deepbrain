import React from 'react';
const gender_map = {0:'不明', 1:'男', 2:'女'};
const parent_map = {0:'无父母信息', 1:'仅有父亲信息',2:'仅有母亲信息', 3:'有父母信息'};

class Input_basic_info extends React.Component{
  constructor(props){
    super(props);
  }

  render(){
    return (
      <div className='input_info'>
        <p>
          <span>性别：{gender_map[this.props.input_info.gender]}</span>
          <span>年龄：{this.props.input_info.age?this.props.input_info.age:'不明'}</span>
        </p>
        <p>父母信息：{parent_map[this.props.input_info.parents_gene_info]}</p>
        <p>表型信息：{this.props.input_info.input_pheno}</p>
      </div>
    )
  }
}

Input_basic_info.propTypes={

}

export default Input_basic_info;
