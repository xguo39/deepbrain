
Genonova
==============================
The backend is running on [Django](https://www.djangoproject.com/)

----------------------------------------------------------------------------------------------
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Configuration](#configuration)
  - [Pre-requisites](#pre-requisites)
- [Docs](#docs)
  - [API doc](#api-doc)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
----------------------------------------------------------------------------------------------

Configuration
--------------
### Pre-requisites
* Run in local terminal
* [Python VirtualEnv Install](https://virtualenv.pypa.io/en/stable/installation/)
### Download repo and install
```bash
# Downlod git repo
git clone git@github.com:xguo39/deepbrain.git
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
python manage.py migrate
python manage.py runserver
```

Docs
--------------
### API doc
<<<<<<< HEAD
Please refer to [docs/APIs.md](https://github.com/xguo39/deepbrain/blob/front-end/docs/APIs.md)
=======
Please refer to [docs/APIs.md](https://github.com/xguo39/deepbrain/blob/master/docs/APIs.md)
>>>>>>> master
