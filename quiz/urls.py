# By Zhufyak V.V
# zhufyakvv@gmail.com
# github.com/zhufyakvv
# 26.06.2017

from django.conf.urls import url

from quiz import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'quiz/(?P<current_id>[0-9])', views.run),
    url(r'login', views.login),
    url(r'logout', views.logout),
    url(r'signup', views.signup),
    url(r'profile/(?P<id>[0-9])', views.profile),
    url(r'profile', views.profile),
    url(r'info_change', views.info_change),
    url(r'password_change', views.password_change),
    url(r'quiz', views.quiz_board),
]
