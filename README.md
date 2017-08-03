<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Deepbrain](#deepbrain)
    - [run in local](#run-in-local)
- [dowload redis](#dowload-redis)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Deepbrain 
### run in local

# dowload redis
1. brew install redis
# install according to requirements.txt
2. pip install -r requirements.txt
# go to the /src in the redis folder, and run
3. ./redis-server (or brew services start redis)
# open another terminal and run
4. celery -A deepbrain beat -l info
# open another terminal and run
5. celery -A deepbrain worker -l info

6. change settings.py database part
7. python manage.py migrate
8. python manage.py runserver
