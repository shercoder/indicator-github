#!/usr/bin/env python

from github import Github
import os
import exceptions
import getpass
import webbrowser
import urllib
import requests
import json
import appindicator
import gtk

def find_token(items):
  for d in items:
    if d['app']['name'] == 'indicator-github':
      return d['token']
  else:
    raise KeyError

client_id = '17d74debb1b3ef6337e6'
redirect = 'http://pyrated.github.io/indicator-github/'
request_string = 'https://github.com/login/oauth/authorize?client_id=%s&redirect_uri=%s&scope=%s'
scope = ''

app_folder = os.path.expanduser(os.path.join('~','.indicator-github',''))
if not os.path.exists(app_folder): os.makedirs(app_folder)

# Check if user has authenticated app
if not os.path.isfile(os.path.join(app_folder,'oauth')):
  # Authorize indicator-github
  webbrowser.open(request_string % (urllib.quote(client_id), urllib.quote(redirect), urllib.quote(scope)))

  # Get oauth tokens
  session = requests.Session()
  session.auth = (raw_input('username:'), getpass.getpass())
  request = session.get('https://api.github.com/authorizations')
  auths = json.loads(request.content)

  try:
    token = find_token(auths)
  except:
    # User didn't authorize app
    print 'Can\'t find token'

  token_file = open(os.path.join(app_folder,'oauth'), 'w+')
  token_file.write(token)
  token_file.close()

# Auth token already exists
else:
  token_file = open(os.path.join(app_folder,'oauth'), 'r')
  token = token_file.read()

# Log user into github
gh = Github(login_or_token=token, client_id=client_id, user_agent=client_id)

indicator = appindicator.Indicator ('indicator-github',\
  os.path.join(os.getcwd(),'gh.png'),\
  appindicator.CATEGORY_COMMUNICATIONS)

indicator.set_status(appindicator.STATUS_ACTIVE)

menu = gtk.Menu()

menu_item = gtk.MenuItem(gh.get_user().name)
menu.append(menu_item)

menu.append(gtk.SeparatorMenuItem())

repo_item = gtk.MenuItem("Repositories")
repo_menu = gtk.Menu()
repo_item.set_submenu(repo_menu)

for repo in gh.get_user().get_repos():
  menu_item = gtk.MenuItem(repo.name)
  repo_menu.append(menu_item)

menu.append(repo_item)

menu.append(gtk.SeparatorMenuItem())

menu_item = gtk.MenuItem("About...")
menu.append(menu_item)

menu_item = gtk.MenuItem("Quit")
menu_item.connect("activate", gtk.mainquit)
menu.append(menu_item)

menu.show_all()
indicator.set_menu(menu)
gtk.main()
