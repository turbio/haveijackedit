from django.shortcuts import render
from django.conf import settings as djangosettings
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.files import File
from .models import *
from urllib.parse import urlparse
import urllib.request
import urllib.parse
import json
import hashlib
import time
import datetime
import io
from .data_uri import DataURI
from datetime import timedelta
from random_words import RandomWords
from django.core.files.temp import NamedTemporaryFile

def scoreJack(jackObject):
	score = 100
	score += (len(jackObject.comment) / 160) * 50
	score += -pow(abs((timezone.now() - jackObject.date).total_seconds()) / (60 * 60), 3) * 2
	votes = 0 #jackVotes(jackObject)
	if votes > 0:
		score += pow(votes, 2) * 100
	else:
		score += votes * 100
	return score

# Create your views here.
def index(request):
	hotJacks = Jack.objects.order_by('date').reverse().filter(
		user__settings__on_homepage = True,
		user__settings__private = False)

	try:
		userObject = user.objects.get(id = request.session['user_id'])
	except:
		userObject = None

	if hotJacks.count() > 0:
		hotJacks = hotJacks
		hotJacks = sorted(hotJacks, key=scoreJack, reverse=True)
	else:
		hotJacks = None

	context = {
		'version': djangosettings.APP_VERSION,
		'show_username': True,
		'jack_list': hotJacks,
		'host': "haveijackedit.com",
		'signed_in': 'user_logged_in' in request.session,
	}

	if request.method == 'GET':
		if 'u' in request.GET:
			context['claim_url'] = request.GET['u']

	if 'user_logged_in' in request.session:
		context['user_analytic_id'] = request.session['user_name']

	subdomain = getSubdomain(request.META['HTTP_HOST'])
	if subdomain:
		return feed(request)
	else:
		return render(request, 'index/index.html', context)

def handlevote(request):
	jackObject = Jack.objects.get(id = request.POST['jack'])

	userChoice = 0
	if request.POST['points'] == 'd':
		userChoice = -1
	elif request.POST['points'] == 'u':
		userChoice = 1
	elif request.POST['points'] == 'n':
		userChoice = 0

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		clientIp = x_forwarded_for.split(',')[0]
	else:
		clientIp = request.META.get('REMOTE_ADDR')

	#first determine if user is logged in
	if 'user_logged_in' in request.session:
		userObject = User.objects.get(id = request.session['user_id'])

		try:
			voteObject = Vote.objects.get(jack=jackObject, user=userObject)
		except:
			voteObject = Vote(jack=jackObject, user=userObject)

		voteObject.ip = getUserIp(request)
		voteObject.date = datetime.datetime.today()
		voteObject.points = userChoice
		voteObject.save()

		replyObject = [{
			'jack': jackObject.id,
			'votes': jackObject.votes()
		}]
		return HttpResponse(json.dumps(replyObject))

	return HttpResponse('lmao')

def settings(request):
	if not 'user_logged_in' in request.session:
		return HttpResponseRedirect('/dash/')

	userObject = user.objects.get(
		id = request.session['user_id']).select_related('settings')
	userSettings = userObject.settings

	user_options = {
		'private': userSettings.private,
		'show_on_home_page': userSettings.on_homepage,
		'show_date': userSettings.show_date,
		'show_time': userSettings.show_time
	}

	context = {
		'version': djangosettings.APP_VERSION,
		'host': "haveijackedit.com",
		'signed_in': 'user_logged_in' in request.session,
		'options': user_options
	}

	if 'user_logged_in' in request.session:
		context['user_analytic_id'] = request.session['user_name']

	return render(request, 'index/settings.html', context)

def submit_settings(request):
	if request.method != 'POST':
		return HttpResponseRedirect('/dash/')

	if not 'user_logged_in' in request.session:
		return HttpResponseRedirect('/dash/')

	userObject = User.objects.get(
		id = request.session['user_id']).select_related('settings')

	if 'submit' in request.POST:
		userSettings = userObject.settings
		userSettings.private = 'private' in request.POST
		userSettings.on_homepage = 'show_on_home_page' in request.POST
		userSettings.show_date = 'show_date' in request.POST
		userSettings.show_time = 'show_time' in request.POST
		userSettings.save()

	if 'delete_account' in request.POST:
		userObject.delete()
		signout(request)

	if 'change_pass' in request.POST:
		try:
			checkCred(userObject.name, request.POST.get('cur_pass', ''))
		except:
			return HttpResponseRedirect('/incorrect_password/')

		pass_salt = createPasswordSalt()
		pass_hash = hashPassword(request.POST.get('new_pass', ''), pass_salt)

		userObject.password_hash = pass_hash
		userObject.password_salt = pass_salt
		userObject.save()

	return HttpResponseRedirect('/settings/')

def signout(request):
	request.session.flush()
	return HttpResponseRedirect('/dash/')

def signin(request):
	context = {
		'version': djangosettings.APP_VERSION,
	}

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

def verifyCaptcha(captcha_response, userIp):
	#information to send to google
	captchaData = {
		'secret': djangosettings.CAPTCHA_KEY,
		'response': captcha_response,
		'remoteip': userIp,
	}
	encodedPostData = urllib.parse.urlencode(captchaData).encode('utf-8')

	captchaRequest = urllib.request.Request(djangosettings.CAPTCHA_URL)
	captchaRequest.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")

	captchaResponse = ''
	with urllib.request.urlopen(captchaRequest, encodedPostData) as f:
		captchaResponse += f.read().decode('utf-8')

	decodedCaptchaResponse = json.loads(captchaResponse)
	if not decodedCaptchaResponse['success']:
		raise Exception('must verify captcha')

def signup(request):
	context = {
		'version': djangosettings.APP_VERSION,
	}

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

			verifyCaptcha(captchaClientResponse, ip)

			createUser(username, password)
			signin(request)
			return HttpResponseRedirect('/dash')
		except Exception as e:
			context['error'] = e.args[0]

	return render(request, 'signup_standalone.html', context)

def feed(request):
	isUser = False
	isPrivate = False
	userJackList = False
	subdomain = getSubdomain(request.META['HTTP_HOST'])

	jacked = False
	try:
		userObject = user.objects.get(
			name__iexact = subdomain).select_related('settings')
		isUser = True

		isPrivate = userObject.settings.private

		if not isPrivate:
			#userJackList = addDetailsToJackList(
				#jack.objects.order_by('date').filter(
					#user = userObject.id).reverse(), userObject)
			day = timedelta(days=1)
			lastJacked = (timezone.now() - userJackList.first().date)
			jacked = lastJacked < day
	except:
		pass

	if jacked:
		try:
			jacked_message = yes_word.objects.order_by('?').first().word
		except:
			jacked_message = "yes"
	else:
		try:
			jacked_message = no_word.objects.order_by('?').first().word
		except:
			jacked_message = "no"

	context = {
		'version': djangosettings.APP_VERSION,
		'show_username': True,
		'host': "haveijackedit.com",
		'jack_list': userJackList,
		'username': subdomain,
		'title_text_a': jacked_message,
		'is_user': isUser,
		'is_private': isPrivate,
		'signed_in': 'user_logged_in' in request.session,
	}

	if 'user_logged_in' in request.session:
		context['user_analytic_id'] = request.session['user_name']

	return render(request, 'index/feed.html', context)

def dash(request):
	#dash is basically useless if you're not logged in, so instead of throwing
	#errors or something, it's easier if we just redirect to the front page
	if not 'user_logged_in' in request.session:
		return HttpResponseRedirect('/')

	username = request.session['user_name']

	context = {
		'version': djangosettings.APP_VERSION,
		'host': "haveijackedit.com",
		'show_date': True,
		'username': username,
		'yes_word': YesWords.objects.random_word('yes'),
		'filler_user': User.objects.order_by('?')[:3],
		'jack_list': Jack.objects.with_details(username),
		'signed_in': 'user_logged_in' in request.session,
	}

	if 'user_logged_in' in request.session:
		context['user_analytic_id'] = request.session['user_name']

	return render(request, 'index/dash.html', context)

#if multiple parts of the application need the user's ip object, this prevents
#multiple database querys
userIpObject = None
def getUserIp(request):
	global userIpObject
	if userIpObject is not None:
		return userIpObject

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		clientIp = x_forwarded_for.split(',')[0]
	else:
		clientIp = request.META.get('REMOTE_ADDR')

	#if an ip alread exists, no need to create another entry for it
	userIpObject, created = Ip.objects.get_or_create(address=clientIp)

	return userIpObject

def submit_jack(request):
	if request.method != 'POST':
		return HttpResponseRedirect('/dash/')

	message = str(request.POST.get('new_jack', ''))
	if message == '':
		return HttpResponseRedirect('/dash/')

	userIp = getUserIp(request)

	newJack = Jack(
		user=User.objects.get(id = request.session['user_id']),
		comment=message,
		date=datetime.datetime.today(),
		ip=userIp)

	if 'jack_geo' in request.POST and not request.POST['jack_geo'] == '':
		recievedGeolocationJson = request.POST['jack_geo']
		recievedGeolocation = json.loads(recievedGeolocationJson)

		newGeolocation = Geolocation(
			ip=userIp,
			lat=recievedGeolocation['lat'],
			lng=recievedGeolocation['long'])
		newGeolocation.save()
		newJack.location = newGeolocation

	if 'image' in request.POST and not request.POST['image'] == '':
		newImage = Image(
			ip=userIp,
			source=request.POST['image_source']
		)
		uri = DataURI(request.POST['image'])
		filename = ''.join([
				word.capitalize()
				for word in RandomWords().random_words(count=5)
			])

		imageFile = NamedTemporaryFile(delete=True)
		imageFile.write(uri.data)
		imageFile.flush()

		newImage.data.save(filename, File(imageFile))
		newImage.save()
		newJack.image = newImage

	if 'jack_link_url' in request.POST and not request.POST['jack_link_url'] == '':
		validUrl = validateUrl(request.POST['jack_link_url'])
		if(validUrl):
			newLink = Link(
				url=validUrl,
				ip=getUserIp(request))
			newLink.save()
			newJack.link = newLink

	newJack.save()

	if 'jack_bro' in request.POST and not request.POST['jack_bro'] == '':
		broStrings = request.POST['jack_bro'].split(",")
		broStrings = [s.strip(' ') for s in broStrings]

		for broString in broStrings:
			newJack.bros.add(User.objects.get(name__iexact=broString))

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

#returns True if a use with username exists, otherwise returns false
def userExists(username):
	return False if User.objects.filter(name__iexact = username).count() == 0 else True

#creates user or raises exception detailing what went wrong
def createUser(username, password):
	if username == '':
		raise Exception('must supply a username')
	if not username.isalnum():
		raise Exception('username must be alphanumeric')
	if userExists(username):
		raise Exception('username already exists')

	hash_salt = createPasswordSalt()
	hashed_password = hashPassword(password, hash_salt)

	newUserSettings = UserSettings()
	newUserSettings.save()

	newUser = User(
		name=username,
		password_hash=hashed_password,
		last_online=datetime.datetime.today(),
		creation_date=datetime.datetime.today(),
		password_salt=hash_salt,
		settings=newUserSettings)
	newUser.save()

def createPasswordSalt():
	return hashlib.md5(str(time.time()).encode()).hexdigest()

def hashPassword(password, salt):
	return hashlib.sha512((salt + password).encode()).hexdigest()

#returns an id if username matches password, otherwise throws an exception
def checkCred(username, password):
	if(username == None or username == ''):
		raise Exception('must provide a username')
	if(password == None or password == ''):
		raise Exception('must provide a password')

	try:
		userObject = User.objects.get(name__iexact = username)
	except:
		raise Exception('incorrect credentials')

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

def addDetailsToJackList(jackList, user=None):
	shade = False
	for j in jackList:
		try:
			jackGeolocation = geolocation.objects.get(jack = j)
			j.lng = jackGeolocation.lng
			j.lat = jackGeolocation.lat
		except:
			pass

		jackImage = image.objects.filter(jack = j)
		#if not jackImage.count() == 0:
			#j.has_image = True
			#j.image_data = jackImage.first().data
			#j.image_source = jackImage.first().source

		jackLink = link.objects.filter(jack = j)
		if not jackLink.count() == 0:
			j.has_link = True
			j.link_url = jackLink.first().url
			j.link_text = jackLink.first().url

		jackBro = jack_bro.objects.filter(jack = j)
		if not jackBro.count() == 0:
			j.has_bro = True
			j.bros = []

		for b in jackBro:
			j.bros.append(b.bro)

		j.shade = shade = not shade

		j.votes = 0
		jackVotes = vote.objects.filter(jack = j)
		for v in jackVotes:
			j.votes += v.points

		if user is not None:
			userJackVote = vote.objects.filter(jack=j, user=user)
			if userJackVote.count() > 0:
				userJackVote = userJackVote.first()
				if userJackVote.points > 0:
					j.vote_up = True
				elif userJackVote.points < 0:
					j.vote_down = True

		jackAgeSeconds = (timezone.now() - j.date).seconds
		jackAgeMinutes = jackAgeSeconds / 60
		jackAgeHours = jackAgeMinutes / 60
		jackAgeDays = jackAgeHours / 24
		if jackAgeMinutes < 1:
			j.age = str(int(jackAgeSeconds)) + " seconds ago"
		elif jackAgeHours < 1:
			j.age = str(int(jackAgeMinutes)) + " minutes ago"
		elif jackAgeDays < 1:
			j.age = str(int(jackAgeHours)) + " hours ago"
		else:
			j.age = str(int(jackAgeDays)) + " days ago"

	return jackList;
