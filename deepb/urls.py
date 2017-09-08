from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = 'deepb'
urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^en/$', views.index_en, name='index_en'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^home/ch$', views.HomeView_ch.as_view(), name='home_ch'),
    url(r'^home/ch/new/?', views.home_new_View_ch, name='home_new_ch'),
    url(r'^home/(?P<show_all>[-\w]+)/$', views.HomeView.as_view(), name='home_all'),
    url(r'^home/(?P<show_all>[-\w]+)/ch$', views.HomeView_ch.as_view(), name='home_all_ch'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^upload/ch$', views.upload_ch, name='upload_ch'),
    url(r'^(?P<pk>[0-9]+)/result/$', views.result, name='result'),
    url(r'^(?P<pk>[0-9]+)/result/ch$', views.result_ch, name='result_ch'),
    url(r'^(?P<pk>[0-9]+)/result/interpretation/$', views.interpretation, name='interpretation'),
    url(r'^(?P<pk>[0-9]+)/result/interpretation/ch$', views.interpretation_ch, name='interpretation_ch'),
    url(r'^chpo$', views.chpo, name='chpo'),
    url(r'^lof$', views.lof, name='lof'),
    url(r'^api/task/new_task/(?P<user_name>[-\w]+)/$', views.new_task.as_view()),
    url(r'^api/task/progress_task_list/(?P<user_name>[-\w]+)/$', views.progress_task_list.as_view()),
    url(r'^api/task/all_task_list/(?P<user_name>[-\w]+)/$', views.all_task_list.as_view()),
    url(r'^api/task/task_check/(?P<user_name>[-\w]+)/$', views.task_check.as_view()),
    url(r'^api/result/(?P<task_id>[0-9]+)/(?P<user_name>[-\w]+)/$', views.case_result.as_view()),
    url(r'^api/result/(?P<task_id>[0-9]+)/(?P<gene_name>[-\w]+)/(?P<user_name>[-\w]+)/$', views.result_detail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
