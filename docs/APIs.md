APIs
======
* Note: if not specified, the default format for request and response is [JSON](http://www.json.org/), so there should be a field `Content-Type: application/json` in the HTTP header of such request.

--------------------------
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Template](#template)
  - [Template Gene_task_form](#template-gene_task_form)
- [Tasks](#tasks)
  - [Upload_task](#upload_task)
  - [Progress_task_list](#progress_task_list)
  - [All_task_list](#all_task_list)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
---------------------------

Template
---
### Template Gene_task_form
```bash
{
 id:"myForm",
 name:"myForm",
 encType:"multipart/form-data",
 input:{
  task_name: text,
  gene_file: file(.txt,.xlsx,.xls,.csv,.vcf),
  input_phen: file(.txt),
  input_text_phenotype:text,
  father_check:boolean,
  father_check_pheno:boolean,
  father_gene_file:file(.txt,.xlsx,.xls,.csv,.vcf),
  mother_check:boolean,
  mother_check_pheno:boolean,
  mother_gene_file:file(.txt,.xlsx,.xls,.csv,.vcf),
  check_incidental_findings:boolean,
  check_candidate_genes:boolean
}
```

Tasks
---
### Upload_task
* Description: For uploading the new task form
* URL: `/api/tasks/new_task`
* Method: `POST`
* Request Example:
```javascript
{
 body:{% Gene_task_form %}
}
```
* Response Example on `success`:
```
http/1.1 200 OK
```
```
{
 success:true,
 data:{
  task_id:’1111…’
 }
}
```
* Response Example on `failure`:
```
http/1.1 200 OK
```
```javascript
{
 success:false,
 errCode:INFOMATION_UNCOMPLETED
}
```

### Progress_task_list
* Description: For fetching the processing task list
* URL: `/api/task/progress_task_list/`
* Method: `GET`
* Request Example”
`{}`
* Response Example on `success`:
```
http/1.1 200 OK
```
```javascript
{
 success:true,
 list:[
  {
    task_name: xiaonan,
    completed_missons: 5,
    total_missions: 10,
    current_misson:“正在处理xxx基因”，
    estimated_time:”5分钟“，
    checked: false
   },
   {
     task_name:tianqi,
     completed_missions:10,
     total_missions:10,
     current_mission:””,
     estimated_time:”4分钟”，
     checked:false
   }, …  
 ]
}
```
* Response Example on `failure`:
```
http/1.1 200 OK
```
```javascript
{
 success:failure,
 errorCode: BACKEND_MAINTAINANCE
} 
```

### All_task_list
* Description: For fetching all the task list
* URL: `/api/task/all_task_list/`
* Method: `GET`
* Request Example
`{}`
* Response Example on `success`:
```
http/1.1 200 OK
```
```javascript
{
 success:true,
 list:[
  {
   id:1,
   name:xiaonan,
   time: '2017-06-18, 12:03pm',
   status:true,
   checked:false
  },
  {
   id:2,
   name:tianqi,
   time: '2017-06-18, 12:03pm',
   status:false,
   checked:true
  }…
 ]
}
```
* Response Example on `failure`:
```
http/1.1 200 OK
```
```javascript
{
 success:false,
 errCode: BACKEND_MAINTANANCE
}
```

### Fetch_case_result
* Description: For fetching the single case result
* URL: `/api/result/:case_id/`
* Method: `GET`
* Request Example
`{}`
* Response Example on `success`:
```
http/1.1 200 OK
```
```javascript
{
 success:true,
 result_data:{
  summary_table_data:[
    {
      gene:'WWOX',
      transcript:'chr16:g.78466583C>G',
      cDNA:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      pheno_matched_score:39,
      ACMG_criteria_matched:"PM2|BP4",
      clinical_significance:'Uncertain Significance',
      clinical_significance_score:55,
      classification_score:0.88,
      total_score:1.8	
    },…
  ],
  incidental_table_data:[
    {
      gene:'WWOX',
      transcript:'chr16:g.78466583C>G',
      cDNA:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      pheno_matched_score:39,
      ACMG_criteria_matched:"PM2|BP4",
      clinical_significance:'Uncertain Significance',
     },…
  ],
  candidate_table_data:[
    {
      gene:'WWOX',
      transcript:'chr16:g.78466583C>G',
      cDNA:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      phenotype_matched:’from paper’
     },…
  ],
  input_gene_data:[
    {
      
     }
  ]
 }
```
* Response Example on `failure`:
```
http/1.1 200 OK
```
```javascript
{
 success:false,
 errCode: BACKEND_MAINTANANCE
}
```











