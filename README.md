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
