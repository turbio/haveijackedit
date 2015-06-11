from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from .models import jack, user
import hashlib
import time
import datetime

# Create your views here.
def index(request):
	userError = False
	if request.method == 'POST':
		try:
			handleUsercredentials(request)
		except:
			userError = "yep"

	latest_jack = jack.objects.order_by('date')
	if len(latest_jack) > 0:
		latest_jack = latest_jack[0]
	else:
		latest_jack = None

	context = {'latest_jack': latest_jack}

	subdomain = getSubdomain(request.META['HTTP_HOST'])
	if subdomain:
		return feed(request)
	else:
		return render(request, 'index/index.html', context)


def feed(request):
	isUser = True
	userJackList = False
	subdomain = getSubdomain(request.META['HTTP_HOST'])

	userId = user.objects.filter(name = subdomain)
	if len(userId) > 0:
		userId = userId[0].id
		userJackList = jack.objects.order_by('date').filter(user_id = userId)
		isUser = True
	else:
		isUser = False

	context = {
		'jack_list': userJackList,
		'username': subdomain,
		'title_text_a': 'lmao',
		'is_user': isUser
	}

	print(str(context))
	return render(request, 'index/feed.html', context)

def dashboard(request):
	username = getSubdomain(request.META['HTTP_HOST'])

	userId = user.objects.filter(name = subdomain)
	if len(userId) > 0:
		userId = userId[0].id
		userJackList = jack.objects.order_by('date').filter(user_id = userId)

	context = { 'jack_list': userJackList,
		'username': username,
	}
	return render(request, 'index/dash.html', context)

def getSubdomain(url):
	splitUrl = url.split('.')

	urlParts = len(splitUrl)

	#for dealing with localhost
	if 'localhost' in splitUrl[-1]:
		urlParts += 1

	if urlParts == 3:
		return splitUrl[0]

	return False

def handleUsercredentials(request):
	username = str(request.POST.get('username', ''))
	password = str(request.POST.get('password', ''))
	action = str(request.POST.get('action', ''))

	if username == '':
		raise Exception('most provide a username')
	if password == '':
		raise Exception('most provide a password')

	if action == 'signup':
		signup(username, password)
	elif action == 'signin':
		print('try...' + action)
		signin(username, password)

def signin(username, password):
	userObject = user.objects.filter(name = username)
	hashed_password = hashlib.sha512(password.encode()).hexdigest()

	if userObject == None:
		raise Exception('incorrect credentials')

	if userObject.password == hashed_password:
		print('success...')
		#TODO this should then log the use in
	else:
		raise Exception('incorrect credentials')

def signup(username, password):
	if not username.isalnum():
		raise Exception('username must be alphanumeric')
	if userExists(username):
		raise Exception('username already exists')

	hash_salt = hashlib.md5(str(time.time()).encode()).hexdigest()
	hashed_password = hashlib.sha512(password.encode()).hexdigest()

	newUser = user(
		name=username,
		password_hash=hashed_password,
		last_online=datetime.datetime.today(),
		creation_date=datetime.datetime.today(),
		password_salt=hash_salt)
	newUser.save()

def userExists(username):
	return False;
