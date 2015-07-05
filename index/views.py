from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import jack, user, yes_word, no_word, geolocation, link, image, jack_bro
from urllib.parse import urlparse
import urllib.request
import urllib.parse
import json
import hashlib
import time
import datetime

# Create your views here.
def index(request):
	#if 'user_logged_in' in request.session:
		#return HttpResponseRedirect('/dash/')

	latest_jack = jack.objects.order_by('date').reverse()
	if len(latest_jack) > 0:
		latest_jack = latest_jack[0]
	else:
		latest_jack = None

	context = {
		'show_username': True,
		'jack': latest_jack,
		'host': "haveijackedit.com",
		'signed_in': 'user_logged_in' in request.session,
	}

	if 'user_logged_in' in request.session:
		context['user_analytic_id'] = request.session['user_name']

	subdomain = getSubdomain(request.META['HTTP_HOST'])
	if subdomain:
		return feed(request)
	else:
		return render(request, 'index/index.html', context)

def signout(request):
	request.session.flush()
	return HttpResponseRedirect('/dash/')

def signin(request):
	context = {}

	if request.method == 'POST':
		username = str(request.POST.get('username', ''))
		password = str(request.POST.get('password', ''))

		try:
			userId = checkCred(username, password)

			request.session['user_logged_in'] = True
			request.session['user_id'] = userId
			request.session['user_name'] = username

			return HttpResponseRedirect('/dash')
		except Exception as e:
			context['error'] = e.args[0]

	return render(request, 'signin_standalone.html', context)


def signup(request):
	context = { }

	if request.method == 'POST':
		username = str(request.POST.get('username', ''))
		password = str(request.POST.get('password', ''))

		try:
			captchaClientResponse = str(request.POST.get('g-recaptcha-response', ''))

			#get the users ip
			x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
			if x_forwarded_for:
				ip = x_forwarded_for.split(',')[0]
			else:
				ip = request.META.get('REMOTE_ADDR')

			#information to send to google
			captchaData = {
				'secret': settings.CAPTCHA_KEY,
				'response': captchaClientResponse,
				'remoteip': ip,
			}
			encodedPostData = urllib.parse.urlencode(captchaData).encode('utf-8')

			captchaRequest = urllib.request.Request(settings.CAPTCHA_URL)
			captchaRequest.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")

			captchaResponse = ''
			with urllib.request.urlopen(captchaRequest, encodedPostData) as f:
				captchaResponse += f.read().decode('utf-8')

			decodedCaptchaResponse = json.loads(captchaResponse)
			if not decodedCaptchaResponse['success']:
				raise Exception('must verify captcha')

			createUser(username, password)
			signin(request)
			return HttpResponseRedirect('/dash')
		except Exception as e:
			context['error'] = e.args[0]

	return render(request, 'signup_standalone.html', context)

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
		'show_username': True,
		'host': "haveijackedit.com",
		'jack_list': userJackList,
		'username': subdomain,
		'title_text_a': 'lmao',
		'is_user': isUser,
		'signed_in': 'user_logged_in' in request.session,
	}

	if 'user_logged_in' in request.session:
		context['user_analytic_id'] = request.session['user_name']

	return render(request, 'index/feed.html', context)

def dashboard(request):
	if not 'user_logged_in' in request.session:
		return HttpResponseRedirect('/')

	username = request.session['user_name']

	userId = user.objects.filter(name = username).first()
	userJackList = jack.objects.order_by('date').filter(user_id = userId).reverse()

	yesWord = yes_word.objects.order_by('?').first()

	if yesWord == None:
		yesWord = 'yes'
	else:
		yesWord = yesWord.word

	context = {
		'host': "haveijackedit.com",
		'show_date': True,
		'username': username,
		'yes_word': yesWord,
		'jack_list': userJackList,
		'signed_in': 'user_logged_in' in request.session,
	}

	if 'user_logged_in' in request.session:
		context['user_analytic_id'] = request.session['user_name']

	return render(request, 'index/dash.html', context)

def new_jack(request):
	if request.method != 'POST':
		return HttpResponseRedirect('/dash/')

	message = str(request.POST.get('new_jack', ''))
	if message == '':
		return HttpResponseRedirect('/dash/')

	userObject = user.objects.filter(id = request.session['user_id']).first()

	newJack = jack(
		user_id=userObject,
		comment=message,
		date=datetime.datetime.today())
	newJack.save()

	print(str(request.POST))

	if 'jack_geo' in request.POST and not request.POST['jack_geo'] == '':
		recievedGeolocationJson = request.POST['jack_geo']
		recievedGeolocation = json.loads(recievedGeolocationJson)

		newGeolocation = geolocation(
			jack=newJack,
			lat=recievedGeolocation['lat'],
			lng=recievedGeolocation['long'])
		newGeolocation.save()

	if 'image' in request.POST and not request.POST['image'] == '':
		newImage = image(
			jack=newJack,
			data=request.POST['image'])
		newImage.save()

	if 'jack_link_url' in request.POST and not request.POST['jack_link_url'] == '':
		validUrl = validateUrl(request.POST['jack_link_url'])
		if(validUrl):
			newLink = link(
				jack=newJack,
				url=validUrl)
			newLink.save()

	if 'jack_bro' in request.POST and not request.POST['jack_bro'] == '':
		broStringList = request.POST['jack_bro'].split(",")
		broStringList = [s.strip(' ') for s in broStringList]

		for b in broStringList:
			bro = user.objects.filter(name = b)
			if not len(bro) <= 0:
				newJackBro = jack_bro(
					jack=newJack,
					bro=bro.first())
				newJackBro.save()

	return HttpResponseRedirect('/dash/')

def getSubdomain(url):
	splitUrl = url.split('.')

	urlParts = len(splitUrl)

	#for dealing with localhost
	if 'localhost' in splitUrl[-1]:
		urlParts += 1

	if urlParts == 3:
		return splitUrl[0]

	return False

#def handleUsercredentials(request):
	#username = str(request.POST.get('username', ''))
	#password = str(request.POST.get('password', ''))
	#action = str(request.POST.get('action', ''))

	#if username == '':
		#raise Exception('most provide a username')
	#if password == '':
		#raise Exception('most provide a password')

	#if action == 'signup':
		##check captcha
		#captchaClientResponse = str(request.POST.get('g-recaptcha-response', ''))
		#x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		#if x_forwarded_for:
			#ip = x_forwarded_for.split(',')[0]
		#else:
			#ip = request.META.get('REMOTE_ADDR')
		#post_data = [
			#('secret', settings.CAPTCHA_KEY),
			#('response', captchaClientResponse),
			#('remoteip', ip),
		#]
		##result = urllib.urlopen('https://www.google.com/recaptcha/api/siteverify', urllib.urlencode(post_data))
		##content = result.read()
		##print(content)
		#signup(username, password)
	#elif action == 'signin':
		#userId = signin(username, password)
		#request.session['user_logged_in'] = True
		#request.session['user_id'] = userId
		#request.session['user_name'] = username

#returns True if a use with username exists, otherwise returns false
def userExists(username):
	userObject = user.objects.filter(name = username)
	if len(userObject) == 0:
		return False
	else:
		return True

#creates user or raises exception detailing what went wrong
def createUser(username, password):
	if username == '':
		raise Exception('must supply a username')
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

#returns an id if username matches password, otherwise throws an exception
def checkCred(username, password):
	if(username == None or username == ''):
		raise Exception('must provide a username')
	if(password == None or password == ''):
		raise Exception('must provide a password')

	userObject = user.objects.filter(name = username)
	if len(userObject) == 0:
		raise Exception('incorrect credentials')
	else:
		userObject = userObject[0]

	hashed_password = hashlib.sha512((
		userObject.password_salt + password).encode()).hexdigest()

	if userObject.password_hash == hashed_password:
		return userObject.id
	else:
		raise Exception('incorrect credentials')

def validateUrl(url):
	#first check if it has a scheme
	#if it does not, assume http by adding http://
	if(not urlparse(url).scheme):
		url = 'http://' + url

	validate = URLValidator()
	try:
		validate(url)
	except:
		return False

	return url
