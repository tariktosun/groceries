# for returning pages to the user
from django.http import HttpResponse
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from models import * # for model creation
import re # for hashtag, mention and youtube url pattern matching
# for pulling settings from environment variables and settings.py
from os import getenv
from django.conf import settings
# for generating random authentication strings
import string
from random import choice
import requests # for facebook OAuth HTTP requests
from facepy import GraphAPI # for facebook API requests
from datetime import datetime, timedelta # for checking expiry of
# OAuth tokens
from django.db.utils import IntegrityError # for catching db errors
import smtplib # for sending email
# for formatting new user email
from email.utils import formatdate
from django.contrib.contenttypes.models import ContentType
from urllib import quote
from itertools import chain # for dealing with lists in directory
from django.db.models import Q # for search

### --------------- Groceries stuff begins here  -------------------- ###
def groc_drop(request):
    """ Drop page for groceries. """
    return render_to_response('groc_splash.html')
    #return render_to_response('bootstrap.html')
def initializeLists(request):
  """ Initialize ShoppingList and SuggestionList. Should only be called ONCE. """
  #if request.method != 'POST':
  #  return HttpResponse
  suggestionList = SuggestionList()
  shoppingList = ShoppingList()

  try:
    suggestionList.save()
  except IntegrityError:
    return error(request, 'Database Error: SuggestionList creation failed.')
  try:
    shoppingList.save()
  except IntegrityError:
    return error(request, 'Database Error: ShoppingList creation failed.')
  #  
  return render_to_response('groc_splash.html')

def renderGrocHomepage(request):
  """ Renders homepage for groceries. """
  # items:
  items = Item.objects.all()
  items = list(items)
  # suggestionList:
  suggestionList = SuggestionList.objects.all() # comes out as a queryDict (I think...)
  suggestionList = suggestionList[0] # there's only one.
  suggestionList = list(suggestionList.items.order_by('-frequency')) # Pull out the items.
  # shoppingList:
  shoppingList = ShoppingList.objects.all()
  shoppingList = shoppingList[0] 
  shoppingList =list(shoppingList.items.all())
  c = RequestContext(request, {'items':items, 'suggestionListItems':suggestionList, 'shoppingListItems':shoppingList})
  return render_to_response('groc_home.html', c)

def addNewItem(request):
  """ Add an item to the shopping list, and item list. """
  if request.method != 'POST':
    return HttpResponse

  # Item info:
  name = request.POST.get('itemName', '')
  newItem = Item( name = name,
                  frequency = 0)
  # save:
  try:
    newItem.save()
  except IntegrityError:
    return error(request, 'Database Error: Item Creation failed.')

  # add to shopping list:
  shoppingList = ShoppingList.objects.all()
  shoppingList = shoppingList[0] 
  shoppingList.items.add(newItem)

  return renderGrocHomepage(request);

def addFromSuggestions(request):
  """ Adds a new item to the shopping list from the suggestion list, and
  removes item from suggestion list. """
  if request.method != 'POST':
    return HttpResponse

  # get item:
  pk = request.POST.get('itemPK')
  item = Item.objects.filter(pk = pk)[0]
  # add to list:
  shoppingList = ShoppingList.objects.all()[0]
  shoppingList.items.add(item)
  # remove from list:
  suggestionList = SuggestionList.objects.all()[0]
  suggestionList.items.remove(item)
  # # save:
  # try:
  #   newItem.save()
  # except IntegrityError:
  #   return error(request, 'Database Error: Item Creation failed.')

  # # add to shopping list:
  # shoppingList = ShoppingList.objects.all()
  # shoppingList = shoppingList[0] 
  # shoppingList.items.add(newItem)

  return renderGrocHomepage(request);

def archiveShoppingList(request):
  """ Archives the shopping list: Adds 1 to frequency of all items in shopping list, and removes
  all items from shoppingList.  Then, repopulates the suggestion list."""
  if request.method != 'POST':
    return HttpResponse
  # Delete each item from shopping list, and add 1 to its frequency.
  shoppingList = ShoppingList.objects.all()
  shoppingList = shoppingList[0] 
  for item in  shoppingList.items.all():
    item.frequency = item.frequency + 1
    try:
      item.save()
    except IntegrityError:
      return error(request, 'Database Error: Item freq increment failed.')
    shoppingList.items.remove(item)
  # try:
  #   shoppingList.save()
  # except IntegrityError:
  #   return error(request, 'Database Error: shoppingList archive saving failed.')

  # Now repopulate the suggestion list:
  populateSuggestions(request)
  return renderGrocHomepage(request)

def populateSuggestions(request):
  """ Populates suggestion list with all items in database, sorted by frequency. """
  suggestionList = SuggestionList.objects.all() # comes out as a queryDict (I think...)
  suggestionList = suggestionList[0]
  # populate with items:
  items = Item.objects.all()
  suggestionList.items = items
  try:
    suggestionList.save()
  except IntegrityError:
    return error(request, 'Database Error: Failed to populate suggestion list.')



### ------------ Groceries stuff ends here -------------------- ###

# Drop page: either render splash or homepage. Visited when the user
# accesses http://siteurl/
def drop(request):
    if request.session.get('logged_in'):
      #return renderHomepage(request)
      return renderLobby(request)
    else:
      return render_to_response('splash.html')

def error(request, text):
  c = RequestContext(request, {'errortext':text})
  return render_to_response('error.html', c)
  

#########################################################
#                    NEW STUFF!!!!!
#########################################################

def inactivateGame(request):
    """ changes the status of a game from active to inactive. """
    if request.method != 'POST':
      return HttpResponse(status=405)
  
    if not request.session.get('logged_in', False):
      return redirect('/fbauth/')

    game_to_inactivate_pk = request.POST.get('game_to_inactivate_pk', '')
    game = Game.objects.filter(pk = game_to_inactivate_pk)[0]
    game.status = 'inac'
    # save it:
    try:
      game.save()
    except IntegrityError:
      return error(request, 'Database Error: Game inactivation failed.')
    return renderLobby(request)


def renderLobby(request):
    """ Renders the lobby """
    if not request.session.get('logged_in', False):
      return redirect('/fbauth/')

    curUser = User.objects.filter(pk = request.session['uid'])[0]

    games_leading = Game.objects.filter(leader=curUser).filter(status='actv').order_by('-creation_time')
    games_playing = curUser.user_joined_games.filter(status='actv').exclude(leader=curUser)
    games_in_history = curUser.user_joined_games.filter()

    lobby_games = Game.objects.filter(status='actv').exclude(pk__in = games_leading).exclude(pk__in = games_playing).order_by('-creation_time')

    # Only want to have games that we are playing in but NOT leading
    #games_playing = [game for game in games_playing if game.leader != curUser]

    c = RequestContext(request, {'games_leading':games_leading, 
                            'games_playing':games_playing,
                            'lobby_games':lobby_games,
                            'games_in_history':games_in_history,
                            'sport_filter':'any',
                            'style_filter':'either',
                            'curUser':curUser})
    return render_to_response('index.html', c)

def renderGameForm(request):
  """ renders dummy game form """
  c = RequestContext(request)
  return render_to_response('gameFormDummy.html', c)

def renderGameList(request):
  """ render all games in dummy feed. """
  # Check user login status
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]
  
  # Fetch all hashtags and posts to display
  posts = UserPost.objects.order_by('-time')
  hashtags = Tag.objects.order_by('-time')

  # Fetch all games
  games = Game.objects.order_by('-creation_time')

  # Games that curUser is leader of
  games_leading = Game.objects.filter(leader=curUser).order_by('-creation_time')
  games_playing = curUser.user_joined_games.all()

  games_playing = [game for game in games_playing if game.leader != curUser]
  
  # Render the feed using the main template
  c = RequestContext(request, {'games_list':games,
                            'games_leading':games_leading,
                            'games_playing':games_playing,
                            'tags_list':hashtags,
                            'curUser':curUser,})
  return render_to_response('gameDisplayDummy.html', c)

def createGame(request):
  """ Create a new game, which curuser leads. """

  # May only be accessed through an HTML POST
  if request.method != 'POST':
      return HttpResponse   
  if not request.session.get('logged_in', False):
      return redirect('/fbauth')
  curUser = User.objects.filter(pk = request.session['uid'])[0]

  # User info:
  game_leader = curUser
  #metadata:
  name = request.POST.get('name', '')
  sport = request.POST.get('sport', '')
  style = request.POST.get('style', '')
  location = request.POST.get('location', '') 
  datetime = request.POST.get('datetime', '')
  min_players = request.POST.get('min_players', '')
  max_players = request.POST.get('max_players', '')

  # create object:
  newGame = Game( leader = game_leader,
                name = name,
                sport = sport,
                location = location,
                game_datetime = datetime,
                style = style,
                min_number_players = min_players,
                max_number_players = max_players,
                status = 'actv'
               )

  # save it:
  try:
      newGame.save()
  except IntegrityError:
      return error(request, 'Database Error: Game creation failed.')

  # add m2m fields (must be done after saving)
  newGame.players.add(game_leader) # leader should also be a player.
  
  return redirect('/lobby/')

def joinGame(request):
  # This page may only be accessed through an HTML POST request
  if request.method != 'POST':
      return HttpResponse(status=405)

  # Get the game object we are joining.  Make sure whatever form we get here
  # from gives this input.
  game_pk = request.POST.get('game_to_join_pk')
  #game_name = request.POST.get('game_to_join_name', '')
  #game = Game.objects.filter(name = game_name)[0]
  game = Game.objects.filter(pk = game_pk)[0]
  curUser = User.objects.filter(pk = request.session['uid'])[0]

  if game.status == 'inac':
    return

  # Check that the current user is not already a player in this game.
  # We should make it so that state can never be reached anyway
  if curUser in game.players.all():
    return

  game.players.add(curUser)

  # TODO: This should redirect to the game page
  return redirect('/lobby/')

def leaveGame(request):
  # This page may only be accessed through an HTML POST request
  if request.method != 'POST':
    return HttpResponse(status=405)

  #game_name = request.POST.get('game_to_leave_name', '')
  game_pk = request.POST.get('game_to_leave_pk', '')
  #game = Game.objects.filter(name = game_name)[0]
  game = Game.objects.filter(pk = game_pk)[0]
  curUser = User.objects.filter(pk = request.session['uid'])[0]

  if game.status == 'inac':
    return

  # Check that the current user is actually a player in this game.
  # We should make it so that can never actually happen
  if not curUser in game.players.all():
    return

  # remove curUser from this game's list of players
  game.players.remove(curUser)
  # If curUser is the leader, delete the game
  # (Not sure if that's how we want to handle that)
  if game.leader == curUser:
    # Check if the game is now empty.  If so, delete.
    if not game.players.all():
      game.delete()
    # Otherwise, make someone else the leader
    else:
      game.leader = game.players.all()[0]
      try:
        game.save()
      except IntegrityError:
        return error(request, 'Database Error: Game creation failed.')

  return redirect('/lobby/')

def deleteGame(request):
  return redirect('/lobby/')


def renderFilteredLobby(request):
  """ Renders the lobby """
  if not request.session.get('logged_in', False):
    return redirect('/fbauth/')

  curUser = User.objects.filter(pk = request.session['uid'])[0]

  games_leading = Game.objects.filter(leader=curUser).filter(status='actv').order_by('-creation_time')
  games_playing = curUser.user_joined_games.filter(status='actv').exclude(leader=curUser)

  sport = request.POST.get('sport', '')
  style = request.POST.get('style', '')
  if sport != 'any' and style != 'either':
    lobby_games = Game.objects.filter(status='actv').filter(sport=sport).filter(style=style).exclude(pk__in = games_leading).exclude(pk__in = games_playing).order_by('-creation_time')
  elif sport != 'any':
    lobby_games = Game.objects.filter(status='actv').filter(sport=sport).exclude(pk__in = games_leading).exclude(pk__in = games_playing).order_by('-creation_time')
  elif style != 'either':
    lobby_games = Game.objects.filter(status='actv').filter(style=style).exclude(pk__in = games_leading).exclude(pk__in = games_playing).order_by('-creation_time')
  else:
    lobby_games = Game.objects.filter(status='actv').exclude(pk__in = games_leading).exclude(pk__in = games_playing).order_by('-creation_time')

  c = RequestContext(request, {'games_leading':games_leading, 
                            'games_playing':games_playing,
                            'lobby_games':lobby_games,
                            'sport_filter':sport,
                            'style_filter':style,
                            'curUser':curUser})
  return render_to_response('index.html', c)



#########################################################
#                      end new stuff.
#########################################################


# ----      Social Feed-based Views       ---- #
    
# Render all posts in the social feed
def renderHomepage(request):
  return renderLobby(request)
  # # Check user login status
  # if not request.session.get('logged_in', False):
  #     return redirect('/fbauth/')
  # curUser = User.objects.filter(pk = request.session['uid'])[0]
  
  # # Fetch all hashtags and posts to display
  # posts = UserPost.objects.order_by('-time')
  # hashtags = Tag.objects.order_by('-time')
  
  # # Render the feed using the main template
  # c = RequestContext(request, {'post_list':posts,
  #                           'tags_list':hashtags,
  #                           'curUser':curUser,})
  # return render_to_response('home.html', c)


# Renders the social feed as a user profile page, filterint so that
# only posts authored by that user will appear.
def renderProfile(request, name):
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]
       
  # Silently redirect back to home if user does not exist. This
  # behavior differs from hashtags as at mentions may refer to
  # non-existent users.
  name = re.split('-', name)
  try:
      profileUser = User.objects.filter(firstname__iexact = name[0]).filter(lastname__iexact = name[1])[0]
  except:
      return redirect('/home/')
      
  # Fetch all posts authored by the profile user
  authoredPosts = UserPost.objects.filter(author=profileUser.pk).order_by('-time')      
  hashtags = Tag.objects.order_by('-time')
  
  c = RequestContext(request, {'post_list':authoredPosts,
                            'tags_list':hashtags,
                            'curUser':curUser, 
                            'profile_view':True,
                            'profile': profileUser,})
  return render_to_response('home.html', c)

# Renders the social feed, filtered so that only posts containing a
# certain hashtag will appear.
# Note: Hashtagging was implemented while referring to code from
# https://github.com/semente/django-hashtags
def renderHashfiltered(request, hashtag):
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]

  # Search for the user provided hashtag. If it does not exist, throw
  # an error
  try:
      T = Tag.objects.get(text = hashtag)
  except:
      return error(request, "Error: Hashtag %s does not exist." % hashtag)
  
  posts = UserPost.objects.filter(Tags = T).order_by('-time')
  hashtags = Tag.objects.all().order_by('-time')
       
  c = RequestContext(request, {'post_list':posts,
                            'tags_list':hashtags,
                            'curUser':curUser, 
                            'tag_view': True, 
                            'hash': hashtag,})
  return render_to_response('home.html', c)


# Render the social feed, filtered so that only posts marked as
# announcments appear.
def renderAnnouncements(request):
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]
  
  # Fetch the posts and display them
  posts = UserPost.objects.filter(announce=True).order_by('-time')
  hashtags = Tag.objects.all().order_by('-time')
  
  c = RequestContext(request, {'post_list':posts,
                            'tags_list':hashtags,
                            'curUser':curUser,
                            'announcements_view': True})
  return render_to_response('home.html', c)


# Render the social feed filtered by a user provided search term.
# Search is case-insensitive and an empty search results in no action.
def search(request):
  # This page may only be accessed through an HTML POST request
  if request.method != 'POST':
      return HttpResponse(status=405)
  
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]
  
  searchTerm = request.POST.get('query', '')
  # If the user did not enter a search term, redirect them back to
  # the homepage
  if searchTerm == '': 
      return redirect('/home/')
  # Fetch a list of posts containing the term in either post text or
  # associated comment text, using a case insensitive search
  containing = UserPost.objects.filter(Q(text__iregex= searchTerm) | Q(comment__text__iregex= searchTerm)).distinct().order_by('-time')
  hashtags = Tag.objects.order_by('-time')

  c = RequestContext(request, {'post_list':containing,
                            'tags_list':hashtags,
                            'curUser':curUser,
                            'search_view':True,
                            'searchTerm':searchTerm,})
  return render_to_response('home.html', c)



# ----      Non-Feed Views       ---- #



# Render a menu page with food options as posted by the food chairs of
# the club
def renderMenu(request):
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]
  
  # Fetch all most posts, most recent first and display:
  menus = MenuPost.objects.order_by('-time')
  c = RequestContext(request, {'menu_list':menus,
                            'curUser':curUser,})
  return render_to_response('menu.html', c)


# Render a directory page with all of the users of the site.
def directory(request):
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]
  
  # Split the users into two groups; those who are facebook friends
  # with the current user and those who are not. The user will be
  # presented with the option to friend those site users who (s)he is
  # not currently friends with.
  members = User.objects.all();
  notfriends = members.exclude(friends__pk=curUser.pk)
  friends = members.filter(friends__pk=curUser.pk)
  for friend in friends:
      friend.isfriend = True
  members = list(chain(friends, notfriends))       
       
  # sort is stable, so first sort by last sort option, then
  # larger sort categories. must be ordered finally by class year
  # for regroup to work in the directory.html template
  members.sort(key = lambda user: user.firstname)
  members.sort(key = lambda user: user.lastname)
  members.sort(key = lambda user: user.year, reverse=True)
       
  c = RequestContext(request, {'members':members,
                            'curUser':curUser,
                            'fbappid':settings.FACEBOOK_APP_ID,})
  return render_to_response('directory.html', c)



# ----      Posting Content       ----#



# Post a new standard post. Standard posts may be announcements or
# not, and may contain hashtags/mentions and embedded youtube videos.
def post(request):
  # This page may only be accessed through an HTML POST request
  if request.method != 'POST':
      return HttpResponse(status=405)
  
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]
  
  # Check user submitted data
  postText = request.POST.get('text', '')
  if postText == '':
      return error(request, 'You must enter text.')
  
  # Create a new post and save it in the database
  newPost = UserPost(text = postText,
                    author = curUser,
                    hasvideo = False,
                    )
  # Handle announcements
  is_announcement = request.POST.get('is_announcement', False)
  if (is_announcement):
      if (curUser.admin != 'BAMF'):
        return error(request, 'Error: Only officers may post announcements')
      newPost.announce=True
  try:
      newPost.save()
  except IntegrityError:
      return error(request, 'Database Error: Posting failed.')
  
  # Parse the post text for hashtags/mentions and embedded vids
  link_tags_mentions(postText, newPost)
  youtube_embed(postText, newPost)
  return redirect('/home/')


# Post a new comment. Comments, like posts, may contain
# hashtags/mentions and embedded youtube videos and are 
# linked to a parent post.
def postComment(request):
  # This page may only be accessed through an HTML POST request
  if request.method != 'POST':
      return HttpResponse(status=405)
  
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]
  
  # Check user submitted data.
  parentPost = request.POST.get('parentPost', '')
  if parentPost == '':
      return error(request, 'Error: Improperly formed post comment HTTP request.')
  commentText = request.POST.get('commenttext', '')
  if commentText == '':
      return error(request, 'You must enter text.')

  # Fetch the comment's parent post
  parentPost = UserPost.objects.get(pk=parentPost)
  
  # Create the comment in the DB
  newComment = Comment(text = commentText,
                     author = curUser,
                     parent = parentPost, 
                     )
  try:
      newComment.save()
  except IntegrityError:
      return error(request, 'Database Error: Comment posting failed')

  # Parse the comment text for hashtags, mentions, and embedded vids
  link_tags_mentions(commentText, newComment)
  youtube_embed(commentText, newComment)
  return redirect('/home/')


# Post a new menu. Only food chairs and administrators can access this view.
def postMenu(request):
  # This page may only be accessed through an HTML POST request
  if request.method != 'POST':
      return HttpResponse(status=405)
  
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]
  
  # Check permissions
  if(curUser.admin != u'FC' and curUser.admin != u'BAMF'):
      return error(request, 'Error: You do not have permission to post menus.') 
  
  # Fetch the text from the user's request and create the menu in the DB
  menutext = request.POST.get('text', '')
  if menutext == '':
      return error(request, 'Error: You may not post an empty menu.')
  newMenu = MenuPost(text = request.POST['text'],
                    author = curUser,
                 )
  try:
      newMenu.save()
  except IntegrityError:
      return error(request, 'Database Error: Menu posting failed.')
  
  return redirect('/menu/')



# ----        Posting Helper Functions          ---- #



# Search post text for an embedded youtube url and post it
# Regex found on StackOverflow
def youtube_embed(text, post):
  hasyoutubeurl = re.compile(r"[?&]v=[\w-]{11}")
  vididlist = hasyoutubeurl.findall(text)
  
  # If multiple URLs are present, only uses the first one
  if len(vididlist) > 0:
      post.youtubeid = vididlist[0][3:]
      post.hasvideo = True
      try:
        post.save()
      except IntegrityError:
        pass


# Search post text for hashtags and mentions and create the necessary
# links in the database
# This code was influenced heavily by code from https://github.com/semente/django-hashtags
def link_tags_mentions(text, post):
  # Hashtags
  hashRe= re.compile(r'#([-_a-zA-Z0-9]{1,24})')
  for h in hashRe.findall(text):
      hashtag, created = Tag.objects.get_or_create(text=h)
      if created:
        try:
            hashtag.save()
        except IntegrityError:
            continue
      try:
        post.Tags.add(hashtag)
        if isinstance(post,Comment):  #add to parent as well
            post.parent.Tags.add(hashtag)
      except IntegrityError:
        continue
      
  # Mentions
  mentRe= re.compile(r'@([A-Za-z]+)-([A-Za-z]+)')
  for m in mentRe.findall(text):
      u = User.objects.filter(firstname__iexact = m[0]).filter(lastname__iexact = m[1])
      if u.count() > 0:
        u = u[0]
        try:
            post.mentions.add(u)
        except IntegrityError:
            continue
     


# ----        Deletion          ---- #


     
# Delete a standard post in response to a click on the delete button
def deletePost(request):
  # This page may only be accessed through an HTML POST request
  if request.method != 'POST':
      return HttpResponse(status=405)
  
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]
  
  # Fetch the post to be deleted
  postid = request.POST.get('post', '')
  if (postid == ''):
      return error(request, 'Error: Badly formed post delete HTTP request.')
  p = UserPost.objects.filter(pk = postid)
  if p.count() == 0:      # if post does not exist... (catch double tap)
      return renderHomepage(request)
  p = p[0]    # p is a queryset
  
  # Check permissions
  if p.author != curUser and curUser.admin != 'BAMF':
      return error(request, 'Error: You may not delete a post you do not own.')
  # If this is the last post with a given tag, delete the tag as well
  for tag in p.Tags.all():
      if tag.post_set.all().count() == 1:
        tag.delete()
  p.delete()
  return redirect('/home/')


# Delete a comment in response to a click on the delete button
def deleteComment(request):
  # This page may only be accessed through an HTML POST request
  if request.method != 'POST':
      return HttpResponse(status=405)
  
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]

  # Fetch the comment to be deleted
  commentid = request.POST.get('comment', '')
  if commentid == '':
      return error(request, 'Error: Badly formed comment delete HTTP request')
  c = Comment.objects.filter(pk = commentid)
  if c.count() == 0:      # if comment does not exist... (catch double tap)
      return redirect('/home/') 
  c = c[0]    # c is a queryset
  
  # Check permissions
  if c.author != curUser and curUser.admin != 'BAMF':
      return error(request, 'Error: You may not delete a comment you do not own.')
  # If this comment is the last post of any type with a given tag,
  # delete the tag as well
  for tag in c.Tags.all():
      # tag is associated with both comment and its parent post
      if tag.post_set.all().count() == 2:
        # if tag is only in text of comment, delete it
        if not r'#' + tag.text in c.parent.text:
            tag.delete()
  c.delete()
  return redirect('/home/')


# Delete a menu in response to a click on the delete button
def deleteMenu(request):
     # This page may only be accessed through an HTML POST request
  if request.method != 'POST':
      return HttpResponse(status=405)
  
  if not request.session.get('logged_in', False):
      return redirect('/fbauth/')
  curUser = User.objects.filter(pk = request.session['uid'])[0]
  
  # Check permissions
  if (curUser.admin != u'FC' and curUser.admin != u'BAMF'):
      return error(request, 'You do not have permission to delete menus.') 
  
  # Fetch the menu to be deleted and delete it
  menuid = request.POST.get('postMenu', '')
  if (menuid == ''):
      return error(request, 'Error: Badly formed menu delete HTTP request')
  p = MenuPost.objects.get(pk = menuid)
  p.delete()
  return redirect('/menu')



# ----      Authentication       ---- #


# THIS IS NOW DEFUNKT!!
# Authenticate user's netid
def signup(request):
     
  # this page should not be accessed by any method other than GET
  if request.method != 'GET':
       return HttpResponse(status=405)
       
  requestnetid = request.GET.get('netid', '')
  if requestnetid == '': # Http GET request has no netid parameter
      return error(request, 'Error: Not a valid signup HTTP request.')
       
  signup_user = User.objects.filter(netid = requestnetid)
  if signup_user.count() == 0: # netid not found in database
      return error(request, 'Error: Given netid is not approved for signup.')
       
  signup_user = signup_user[0]
  if signup_user.authenticated == True:
      return error(request, 'Error: Given netid is already authenticated.')
  
  # provided code does not match code in database or parameter is empty
  if request.GET.get('authcode', '') != signup_user.authcode:
      return error(request, 'Please check that signup link is correct, contains incorrect authentication code.')


  # make necessary changes in database and session
  signup_user.authenticated = True
  try:
      signup_user.save()
  except IntegrityError:
      return error(request, 'Error during new user signup. Please contact a club officer to continue the signup process.')
  request.session['authuser'] = signup_user;
    
  c = RequestContext(request, {'curUser':signup_user})
  return render_to_response('splash.html')

# Reset the user's session. Note: This will not log the user out of
# facebook. To test without multiple users, use anonymous browsing
def logout(request):
  request.session.flush()
  return render_to_response('splash.html')

# Create a new user using data from the NewUser.html form
def createuser(request):
  
  # This function may only be accessed through an HTML POST request
  if request.method != 'POST':
      return HttpResponse
  
  # Check the user's logged in status
  # if not request.session.get('logged_in', False):
  #    return redirect('/fbauth/')
  # curUser = User.objects.filter(pk = request.session['uid'])[0]
  
  # # Check the permissions of the creating user
  # if curUser.admin != 'BAMF':
  #    return error(request, 'Error: Only administrators may create new users.')

  # # New Developer users may not be created
  # if request.POST.get('admin', '') == 'BAMF':
  #    return error(request, 'Error: Get real, son.')

  # Grab the data for the new user from the POST form.
  new_netid = request.POST.get('netid', '')
  new_firstname = request.POST.get('firstname', '')
  new_lastname = request.POST.get('lastname', '')
  new_year = request.POST.get('year', '2012')
  # Generate a random string of letters and numbers for the
  # authentication code.
  new_authcode = "".join([choice(string.letters+string.digits) for x in range(1, 40)])
  new_admin = request.POST.get('admin', '')
  
  # Try saving the user object into the database. If there was an
  # error in the POST form, it will be caught here.
  try:
      User.objects.create(
        netid = new_netid,
        firstname = new_firstname,
        lastname = new_lastname,
        year = new_year,
        authenticated = False,
        authcode = new_authcode,
        admin = new_admin
        )
  except IntegrityError:
      return error(request, 'Error while creating user. Please check submitted fields and ensure that user is not already signed up.')
     
  # code below sets up for signup view code
  # signup_user = User.objects.filter(netid = new_netid) 
  # if signup_user.count() == 0: # netid not found in database
  #    return error(request, 'Error: Given netid is not approved for signup.')
  # Code below adapted from old signup view
  signup_user = User.objects.filter(netid = new_netid)
  if signup_user.count() == 0: # netid not found in database
      return error(request, 'Error: Given netid is not approved for signup.')
       
  signup_user = signup_user[0]
  if signup_user.authenticated == True:
      return error(request, 'Error: Given netid is already authenticated.')
  
  # provided code does not match code in database or parameter is empty
  #if request.GET.get('authcode', '') != signup_user.authcode:
  #   return error(request, 'Please check that signup link is correct, contains incorrect authentication code.')

  # make necessary changes in database and session
  signup_user.authenticated = True
  try:
      signup_user.save()
  except IntegrityError:
      return error(request, 'Error during new user signup. Please contact a club officer to continue the signup process.')
  request.session['authuser'] = signup_user;
    
  c = RequestContext(request, {'curUser':signup_user})
  return render_to_response('splash.html')

  #--- Link stuff...
  # # Create an authentication link and send it out in an email to the
  # # user's netid
  # link = settings.BASE_URI
  # link += 'signup?netid=' + new_netid
  # link += '&authcode=' + new_authcode

  # # REDIRECT TO LINK:
  # return redirect(link)
  #---

  # target_email = new_netid + '@princeton.edu'
  # subject = 'Web F. Site Registration'
  # message = 'Dear ' + new_firstname + ''',

# You have been selected to help create the future of our dear mother on the webbernets.

# Your mission, should you choose to accept it, is to visit the link below

# '''
#    message += link
  
#    # compose a MIME header for the email
#    mime = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
#                             settings.EMAIL_HOST_USER,
#                             target_email,
#                             subject,
#                             formatdate(), message)
  
#    # Uses a workaround found on StackOverflow (Django's default email implementation
#    # is extremely buggy and will not work with TLS)
#    gmail = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
#    gmail.ehlo()
#    gmail.starttls()
#    gmail.ehlo()
#    gmail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
#    gmail.sendmail(settings.EMAIL_HOST_USER, target_email, mime)
#    gmail.close()
  
#    # Return back to the newuser form
#    return newuser(request)

# Create a new user for use with the site
def newuser(request):
  # if not request.session.get('logged_in', False):
  #     return redirect('/fbauth/')
  # curUser = User.objects.filter(pk = request.session['uid'])[0]
  # if curUser.admin != 'BAMF':
  #    return error(request, 'Error: Only administrators may create new users')
  #c = RequestContext(request), {'curUser':curUser,})
  c = RequestContext(request)
  return render_to_response('newuser.html', c)


# Authenticates users using facebook's OAuth protocol
def fbauth(request):
  # this page should not be accessed through any method but GET 
  if request.method != 'GET':
      return HttpResponse(status=405)
  
  # The url for this page, to be passed as a param to facebook for redirection
  facebookredirect =  settings.BASE_URI+ 'fbauth/'
  facebookredirect = quote(facebookredirect, '')
      
  # if already has an active facebook session
  if request.session.get('fb_token', '') != '':
        
      # if the token is not expired, else fall through to acquire a
      # new one
      if request.session.get('fb_expiry', datetime.now()) > datetime.now():
        
        # if logged in (probably reached this page by accident)
        if request.session.get('logged_in', False):
            return renderHomepage(request)

        # if not logged in, look through the database for the fbid in
        # the session
        else:
            # Use the graph API to get the user's fbid
            graph = GraphAPI(request.session['fb_token'])
            visitor_fbid = int(graph.get('me')['id'])
            this_user = User.objects.filter(fbid = visitor_fbid)
            if this_user.count() == 0: # if fbid not in db
              # if user just signed up
              new_user = request.session.get('authuser', '')
              if new_user != '':
               new_user.fbid = visitor_fbid
               new_user.pic = 'https://graph.facebook.com/' + str(visitor_fbid) + '/picture?type=square'
               new_user.largepic = 'https://graph.facebook.com/' + str(visitor_fbid) + '/picture?type=large'
               try:
                 new_user.save()
               except IntegrityError:
                 return error(request, "Error occured during signup. Please contact a club officer to continue the signup process.")
               this_user = new_user
              else:
               return redirect('/newuser/')  # if we don't recognize you, go to sign up page 
               #return error(request, 'You are not authorized to use this site.')
            else:
              this_user = this_user[0] #querydict
              
            # Log the user in and save their info in the session
            request.session['logged_in'] = True
            request.session['uid'] = this_user.pk
              
            # update the user's list of friends
            this_user.friends.add(this_user)
            friendsets = graph.get('me/friends?fields=installed', page=True)
            for friendset in friendsets:
               
              # friendset includes both data (returned data) and
              # paging (iterator urls)
              friendset = friendset['data']
               
              # for each friend returned
              for friend in friendset:

               # if they have approved the webfsite app
               if friend.get('installed', False):
                 friend_user = User.objects.filter(fbid = friend['id'])
                     
                 # and can be found in the database
                 if friend_user.count() == 1:
                       
                     # add them as a friend (doesn't matter if
                     # done twice)
                     this_user.friends.add(friend_user[0])
            return renderHomepage(request)
      
  # if this is a response from facebook with a code to grab a csrf token
  if request.GET.get('code', '') != '' and request.session['fb_csrf']:
      # Check that the request has a valid csrf token that matches
      # the one stored in the session
      if request.session['fb_csrf'] == request.GET.get('state', ''):
            
        # Create a url to exchange the code received for an oauth token
        oauthurl = 'https://graph.facebook.com/oauth/access_token?'
            
        # Add the fb app ID
        oauthurl += 'client_id='
        oauthurl += settings.FACEBOOK_APP_ID
        
        # Add a redirect url, which should point back to this page
        oauthurl += '&redirect_uri='
        oauthurl += facebookredirect
            
        # Add our app's secret, from developer.facebook.com
        oauthurl += '&client_secret='
        oauthurl += settings.FACEBOOK_API_SECRET
            
        oauthurl += '&code='
        oauthurl += request.GET['code']
            
        gettoken = requests.get(oauthurl)
            
        # Body is of format token and expiry time, split into
        # appropriate parts
        tokenized = gettoken.text.split('&')
        token = tokenized[0].split('=')[1]
        expiry = int(tokenized[1].split('=')[1])
        request.session['fb_token'] = token
        request.session['fb_expiry'] = datetime.now() + timedelta(seconds = expiry)
        return redirect('/fbauth/')

  # Create an initial facebook authentication redirect url, a la 
  # https://developers.facebook.com/docs/authentication/server-side/
  facebookurl = 'https://www.facebook.com/dialog/oauth?'
      
  # Add the facebook app ID
  facebookurl += 'client_id='
  facebookurl += settings.FACEBOOK_APP_ID
      
  # Add a redirect url, which must be the same as one indicated in
  # the fb app settings
  facebookurl += '&redirect_uri='
  facebookurl += facebookredirect
      
  # To protect against CSRF, add a key which is then checked later
  facebookurl += '&state='
  fb_csrf = "".join([choice(string.letters+string.digits) for x in range(1, 40)])
  request.session['fb_csrf'] = fb_csrf
  facebookurl += fb_csrf

  # redirect the user to facebook for OAuth
  return redirect(facebookurl)


