"""deepbrain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from deepb.forms import LoginForm
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import never_cache

urlpatterns = [
    url(r'', include('deepb.urls')), 
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}, name='logout'),
    url(r'^password/reset/$', auth_views.password_reset, {'template_name': 'password_reset_form.html'}, name='password_reset'),
    url(r'^password/reset/done/$', auth_views.password_reset_done, {'template_name': 'password_reset_done.html'}, name='password_reset_done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {'template_name': 'password_reset_confirm.html'}, name='password_reset_confirm'),
    url(r'^password/done/$', auth_views.password_reset_complete, {'template_name': 'password_reset_complete.html'}, name='password_reset_complete'),
    url(r'^password/change/$', auth_views.password_change, {'template_name': 'password_change_form.html'}, name='password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done, {'template_name': 'password_change_done.html'}, name='password_change_done'),
]+ static(settings.STATIC_URL, view=never_cache(serve))



