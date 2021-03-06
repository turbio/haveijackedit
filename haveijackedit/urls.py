"""haveijackedit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from index import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	url(r'^dash/$', views.dash),
	url(r'^settings/$', views.settings),
	url(r'^submit_settings/$', views.submit_settings),
	url(r'^signout/$', views.signout),
	url(r'^signin/$', views.signin),
	url(r'^vote/$', views.handlevote),
	url(r'^signup/$', views.signup),
	url(r'^submit_jack/$', views.submit_jack),
	url(r'^modify/$', views.modifyjack),
	url(r'^jack/', views.standalone_jack),
	url(r'^tag_suggestion/$', views.tag_suggestion),
	url(r'^bro_suggestion/$', views.bro_suggestion),
	url(r'^search_suggestion/$', views.search_suggestion),
	url(r'^about/$', views.about),
	url(r'^tags/', views.tags),
	url(r'^tag/', views.tags),
	url(r'^leaderboard/', views.leader_board),
	url(r'^dev/$', views.developer),
	url(r'^app/$', views.app_download),
	url(r'^bros/$', views.bros),
	url(r'^dump/$', views.dataDump),
	url(r'^dump/data.csv$', views.dumpCSV),
	url(r'^dump/data.json$', views.dumpJson),
	url(r'^customize/$', views.customize),
	url(r'^promo/', views.promo),
	url(r'^search/', views.search),
	url(r'^$', views.index),
	url(r'^stats/$', views.stats),
	url(r'^graph/calendar.svg$', views.calendarGraph),
	url(r'^graph/dist.svg$', views.distributionGraph),
	url(r'^graph/freq.svg$', views.frequencyGraph),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
