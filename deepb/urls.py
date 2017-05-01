from django.conf.urls import url
from . import views

app_name = 'deepb'
urlpatterns = [
	url(r'^$', views.to_home, name='to_home'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^(?P<pk>[0-9]+)/result/$', views.result, name='result'),
    # url(r'^waiting/(?P<task_id>[0-9]+)/$', views.waiting_task, name='waiting'),
    # url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    # url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
]