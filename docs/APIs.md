APIs
======
* Note: if not specified, the default format for request and response is [JSON](http://www.json.org/), so there should be a field `Content-Type: application/json` in the HTTP header of such request.

--------------------------
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Template Gene_task_form](#template-gene_task_form)
- [Upload_task](#upload_task)
- [Progress_list](#progress_list)

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
    checked: false
   },
   {
     task_name:tianqi,
     completed_missions:10,
     total_missions:10,
     current_mission:””,
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



