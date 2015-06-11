from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from .models import jack, user, yes_word, no_word
import hashlib
import time
import datetime

# Create your views here.
def index(request):
	userError = False
	if request.method == 'POST':
		try:
			handleUsercredentials(request)
		except Exception as e:
			userError = e.args[0]

	if 'user_logged_in' in request.session:
		return HttpResponseRedirect('dash')

	latest_jack = jack.objects.order_by('date').reverse()
	if len(latest_jack) > 0:
		latest_jack = latest_jack[0]
	else:
		latest_jack = None

	context = {
		'latest_jack': latest_jack,
		'user_error': userError
	}

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
		userJackList = jack.objects.order_by('date').filter(user_id = userId).reverse()
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

def signout(request):
	request.session.flush()
	return HttpResponseRedirect('/')

def dashboard(request):
	if not 'user_logged_in' in request.session:
		return HttpResponseRedirect('')

	username = request.session['user_name']

	userId = user.objects.filter(name = username).first()
	userJackList = jack.objects.order_by('date').filter(user_id = userId).reverse()

	yesWord = yes_word.objects.order_by('?').first().word

	context = {
		'username': username,
		'yes_word': yesWord,
		'jack_list': userJackList,
	}

	return render(request, 'index/dash.html', context)

def new_jack(request):
	if request.method == 'POST':
		message = str(request.POST.get('new_jack', ''))
		if message[-1] == ' ':
			message = message[0:-1]
		if message[-1] == ',':
			message = message[0:-1]

		userObject = user.objects.filter(id = request.session['user_id']).first()

		newJack = jack(
			user_id=userObject,
			comment=message,
			date=datetime.datetime.today())
		newJack.save()
	return HttpResponseRedirect('/dash')

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
		userId = signin(username, password)
		request.session['user_logged_in'] = True
		request.session['user_id'] = userId
		request.session['user_name'] = username

def signin(username, password):
	userObject = user.objects.filter(name = username)
	if len(userObject) == 0:
		raise Exception('incorrect credentials')
	else:
		userObject = userObject[0]
	print('user object created: ' + str(userObject))
	hashed_password = hashlib.sha512((
		userObject.password_salt + password).encode()).hexdigest()
	print('password hashed')

	if userObject.password_hash == hashed_password:
		return userObject.id
	else:
		raise Exception('incorrect credentials')

def signup(username, password):
	if not username.isalnum():
		raise Exception('username must be alphanumeric')
	if userExists(username):
		raise Exception('username already exists')

	hash_salt = hashlib.md5(str(time.time()).encode()).hexdigest()
	hashed_password = hashlib.sha512((hash_salt + password).encode()).hexdigest()

	newUser = user(
		name=username,
		password_hash=hashed_password,
		last_online=datetime.datetime.today(),
		creation_date=datetime.datetime.today(),
		password_salt=hash_salt)
	newUser.save()

def userExists(username):
	userObject = user.objects.filter(name = username)
	if len(userObject) == 0:
		return False
	else:
		return True
