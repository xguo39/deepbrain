from django.conf.urls import url
from . import views

app_name = 'deepb'
urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^en/$', views.index_en, name='index_en'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^home/ch$', views.HomeView_ch.as_view(), name='home_ch'),
    url(r'^home/(?P<show_all>[-\w]+)/$', views.HomeView.as_view(), name='home_all'),
    url(r'^home/(?P<show_all>[-\w]+)/ch$', views.HomeView_ch.as_view(), name='home_all_ch'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^upload/ch$', views.upload_ch, name='upload_ch'),
    url(r'^(?P<pk>[0-9]+)/result/$', views.result, name='result'),
    url(r'^(?P<pk>[0-9]+)/result/ch$', views.result_ch, name='result_ch'),
    url(r'^(?P<pk>[0-9]+)/result/interpretation/$', views.interpretation, name='interpretation'),
    url(r'^(?P<pk>[0-9]+)/result/interpretation/ch$', views.interpretation_ch, name='interpretation_ch'),
    # url(r'^waiting/(?P<task_id>[0-9]+)/$', views.waiting_task, name='waiting'),
    # url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    # url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
]