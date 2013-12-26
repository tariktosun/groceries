from django.conf.urls.defaults import patterns, include, url
from futureapp.views import * 
from django.conf import settings

from os import environ

# Dynamically match hashtags to urls that do not match any other rules
# and pass them to the hash filtered function
# this function influenced by:
# https://github.com/semente/django-hashtags
hashtagged_url = url(
    regex  = '^(?P<hashtag>[-\w]+)/$',
    view = renderHashfiltered,
    name = 'hashtagged_url'
    )

# Main URL patterns, see futureapp.views for more details
urlpatterns = patterns('',
                       url(r'^$',groc_drop),
                       #url(r'^$',drop),
                       url(r'^post/$',post),
                       url(r'^deletePost/$',deletePost),
                       #url(r'^home/$',renderHomepage),
                       url(r'^addItem/$', addNewItem),
                       url(r'^suggestionAdd/$', addFromSuggestions),
                       url(r'^shoppingRemove/$', removeFromShopping),
                       url(r'^suggestionRemove/$', removeFromSuggestions),
                       url(r'^home/$',renderGrocHomepage),
                       url(r'^initLists/$',initializeLists),
                       url(r'^archive/$',archiveShoppingList),
                       url(r'^fbauth/$',fbauth),
                       url(r'^signup/$',signup),
                       url(r'^newuser/$',newuser),
                       url(r'^createuser/$',createuser),
                       url(r'^directory/$',directory),
                       url(r'^menu/$',renderMenu),
                       url(r'^postMenu/$',postMenu),
                       url(r'^announcements/$',renderAnnouncements),
                       url(r'^deleteMenu/$',deleteMenu),
                       url(r'^logout/$',logout),
                       url(r'^postComment/$',postComment),
                       url(r'^deleteComment/$',deleteComment),
                       url(r'^user/(\w+-\w+)/$', renderProfile),
                       url(r'^search/$', renderHomepage),
                       url(r'^search/$', search),
                       url(r'^lobby/$',renderLobby),
                       url(r'^gameForm/$',renderGameForm),
                       url(r'^createGame/$',createGame),
                       url(r'^gameDisplayDummy/$',renderGameList),
                       url(r'^joinGame/$',joinGame),
                       url(r'^leaveGame/$',leaveGame),
                       url(r'^deleteGame/$',deleteGame),
                       url(r'^inactivateGame/$',inactivateGame),
                       url(r'^renderFilteredLobby/$', renderFilteredLobby),
                       hashtagged_url,
                       )

# URL patterns for static files (images, css, javascript)

if environ.has_key('FUTURE_DIR'):
    # local
  urlpatterns += patterns('',
                         (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
                         )
else:
  urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
  )

