APIs
======
* Note: if not specified, the default format for request and response is [JSON](http://www.json.org/), so there should be a field `Content-Type: application/json` in the HTTP header of such request.

--------------------------
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Template](#template)
  - [Template Gene_task_form](#template-gene_task_form)
<<<<<<< HEAD
=======
  - [Template Review_task_form](#template-review_task_form)
>>>>>>> master
- [Tasks](#tasks)
  - [Upload_task](#upload_task)
  - [Progress_task_list](#progress_task_list)
  - [All_task_list](#all_task_list)
  - [Checked_change](#checked_change)
  - [Fetch_case_result](#fetch_case_result)
  - [Fetch_Annotation](#fetch_annotation)
<<<<<<< HEAD
=======
  - [Fetch Review list](#fetch-review-list)
  - [Upload Result Review](#upload-result-review)
>>>>>>> master

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
<<<<<<< HEAD
  father_check:boolean,
  father_check_pheno:boolean,
  father_gene_file:file(.txt,.xlsx,.xls,.csv,.vcf),
  mother_check:boolean,
  mother_check_pheno:boolean,
  mother_gene_file:file(.txt,.xlsx,.xls,.csv,.vcf),
  check_incidental_findings:boolean,
  check_candidate_genes:boolean
=======
  check_father:boolean,
  check_father_pheno:boolean,
  father_gene_file:file(.txt,.xlsx,.xls,.csv,.vcf),
  check_mother:boolean,
  check_mother_pheno:boolean,
  mother_gene_file:file(.txt,.xlsx,.xls,.csv,.vcf),
  check_incidental_findings:boolean,
  check_candidate_genes:boolean,
  patient_age:12,
  patient_gender:0,
}
```

### Template Review_task_form
```bash
{
  molecular_diagnosis:'',
  pheno_match:false,
  pathogenic:false
>>>>>>> master
}
```

Tasks
---
### Upload_task
* Description: For uploading the new task form
<<<<<<< HEAD
* URL: `/api/task/new_task/:user_name`
=======
* URL: `/api/task/new_task/:user_name/`
>>>>>>> master
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
```javascript
{
 success:true
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
<<<<<<< HEAD
* URL: `/api/task/progress_task_list/:user_name`
=======
* URL: `/api/task/progress_task_list/:user_name/`
>>>>>>> master
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
    id:1,
    task_name: 'xiaonan',
    status:'正在处理xxx基因',
    pub_date: '2017-06-18, 12:03pm',
    processed_time:'5分钟',
    checked: false
   },
   {
     id:2,
     task_name:'tianqi',
     pub_date: '2017-06-18, 12:03pm',
<<<<<<< HEAD
     status:'success',
=======
     status:'succeed',
>>>>>>> master
     estimated_time:'4分钟',
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
 success:false,
 errorCode: BACKEND_MAINTAINANCE
}
```

### All_task_list
* Description: For fetching all the task list
<<<<<<< HEAD
* URL: `/api/task/all_task_list/:user_name`
=======
* URL: `/api/task/all_task_list/:user_name/`
>>>>>>> master
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
   task_name:"xiaonan",
   pub_date: '2017-06-18, 12:03pm',
<<<<<<< HEAD
   status:'success',
   processed_time:'0'
=======
   status:'succeed',
   processed_time:'0',
>>>>>>> master
   checked:false
  },
  {
   id:2,
   task_name:"tianqi",
   pub_date: '2017-06-18, 12:03pm',
   status:'xxxxxxxx fail',
<<<<<<< HEAD
   processed_time:'0'
=======
   processed_time:'0',
>>>>>>> master
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


### Checked_change
* Description: Changing the check status
<<<<<<< HEAD
* URL: `/api/task/task_check/:user_name`
* Method: `PUT`
* Request Example
`{
  id:1
=======
* URL: `/api/task/task_check/:user_name/`
* Method: `PUT`
* Request Example
`{
  task_id:1
>>>>>>> master
  }`
* Response Example on `success`:
```
http/1.1 200 OK
```
```javascript
{
  success:true
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
* URL: `/api/result/:task_id/:user_name/`
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
      transcript:'NM_002834.4',
      variant:'c.922A>G',
      protein:'danbaizhi',
      zygosity:'peixing',
      correlated_phenotypes:'biaoxingpipei',
      pheno_match_score:3.59,
      hit_criteria:"PM2|BP4",
      pathogenicity:'Uncertain Significance',
      pathogenicity_score:0.88,
      final_score:1.8
    },…
  ],
  incidental_table_data:[
    {
      gene:'WWOX',
      transcript:'chr16:g.78466583C>G',
      variant:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      pheno_match_score:39,
      hit_criteria:"PM2|BP4",
      pathogenicity:'Uncertain Significance',
     },…
  ],
  candidate_table_data:[
    {
      gene:'WWOX',
      transcript:'chr16:g.78466583C>G',
      variant:'GCGTG',
      protein:'danbaizhi',
      zygosity:'peixing',
      correlated_phenotypes:’from paper’
     },…
  ],
  input_gene_data:[
    {

     }
  ],
  input_info:{
    age:32, // null if not
    gender:0, // 0 not know, 1 male, 2 female
    input_pheno:'sdfdsfkjsfkjsdhfksjdlf',
    parents_gene_info:0 //0 neither, 1 only father, 2 only mother, 3 both
  },
  interpretation_data:[
    {
      gene:'WWT7',
      variant:'dsfsdfsf',
      criteria:'dfsfsdfsdf',
      interpretation:''
    },...
   ]
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
 errCode: BACKEND_MAINTANANCE
}
```


### Fetch_Annotation
* Description: For fetching the current gene's annotation
* URL: `/api/result/:task_id/:gene_name/:user_name/`
* Method: `Post`
* Request Example:
```javascript
`{
  cDNA:'c.5224G&t>C'
 }`
```
* Response Example on `success`:
```
http/1.1 200 OK
```
```
{
 success:true,
 result_detail:[
   {
     criteria:'PM2',
     interpretation:'dkfslkdfjsldfjlksfjlksdjflksdjflksdj'
   },...
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
 errCode:INFOMATION_UNCOMPLETED
}
```


### Fetch Review list
* Description: For fetching the un-review list
* URL: `/api/review/list/:user_name`
* Method: `Get`
* Request Example:
```javascript
`{}`
```
* Response Example on `success`:
```
http/1.1 200 OK
```
```
{
  success:true,
  review_list:[
    {
      id:1,
      task_name:"xiaonan",
      pub_date: '2017-06-18, 12:03pm',
      status:'succeed',
    },...
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
   errCode:INFOMATION_UNCOMPLETED
}
```

### Upload Result Review
* Description: For uploading the result review task
* URL:`/api/review/upload/:task_id/:user_name`
* Method:`POST`
* Request Example:
```javascript
{
 body:{% Review_task_form %}
}
```
* Response Example on `success`:
```
http/1.1 200 OK
```
```
{
  success:true
}
```
* Response Example on `failure`:
```
http/1.1 200 OK
```
```
{
  success:false
}
```
