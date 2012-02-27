from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('quiz.views',
                       (r'^$', 'index'),
                       #(r'^play/$', 'show_new_question'),
                       (r'^dashboard/$', 'dashboard'),
                       (r'^your-attempts/$', 'show_player_attempts'),
                       (r'^see-answers/$', 'show_answers'),
                       (r'^play/$', 'quiz_not_active'),
                       #(r'^dashboard/$', 'quiz_not_active'),
                       (r'^share-on-facebook/(?P<fb_share_key>.*)/$', 'share_rank'),
                       )
