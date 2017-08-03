
Genonova
==============================
The backend is running on [Django](https://www.djangoproject.com/)

----------------------------------------------------------------------------------------------
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Configuration](#configuration)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
----------------------------------------------------------------------------------------------

Configuration
--------------
* Run in local terminal
```bash
# Dowload redis
brew install redis
# Install according to requirements.txt
pip install -r requirements.txt
# Go to the /src in the redis folder, and run
./redis-server (or brew services start redis)
# Open another terminal and run
celery -A deepbrain beat -l info
# Open another terminal and run
celery -A deepbrain worker -l info
change settings.py database part
# Lauch the django runtime
7. python manage.py migrate
8. python manage.py runserver
```