from django.shortcuts import render
from django.http import Http404
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
import io
from .data_uri import DataURI
from random_words import RandomWords
from django.core.files.temp import NamedTemporaryFile
from datetime import datetime, timezone, timedelta, date
from decorator import decorator

@decorator
def paginate(func, request, *args, **kwargs):
	currentPageNumber = request.GET.get('page', 1)
	try:
		currentPageNumber = int(currentPageNumber)
	except:
		currentPageNumber = 1

	nextPageNumber = currentPageNumber + 1
	prevPageNumber = currentPageNumber - 1 if currentPageNumber > 1 else False

	if not hasattr(request, 'context'):
		request.context = {}

	request.context['current_page'] = \
			currentPageNumber if currentPageNumber >= 1 \
			else 1
	request.context['page_next'] = nextPageNumber
	request.context['page_prev'] = prevPageNumber

	return func(request, *args, **kwargs)

@decorator
def communitypage(func, request, *args, **kwargs):
	if not hasattr(request, 'context'):
		request.context = {}
	request.context['is_community_page'] = True
	return func(request, *args, **kwargs)

@decorator
def searchable(func, request, *args, **kwargs):
	if not hasattr(request, 'context'):
		request.context = {}
	request.context['is_searchable'] = True
	return func(request, *args, **kwargs)

@decorator
def sortable(func, request, *args, **kwargs):
	if not hasattr(request, 'context'):
		request.context = {}
	request.context['is_sortable'] = True
	return func(request, *args, **kwargs)

@decorator
def handlesubdomain(func, request, *args, **kwargs):
	subdomain = getSubdomain(request.META['HTTP_HOST'])
	if subdomain:
		if request.META['PATH_INFO'] == '/':
			return feed(request)
		else:
			return HttpResponseRedirect('/')

	return func(request, *args, **kwargs)

def jackSortMethod(request, default):
	sortMethods = {
		'popular': 'score',
		'top': 'votes',
		'new': 'date',

		'score': 'score',
		'votes': 'votes',
		'date': 'date'
	}

	return sortMethods.get(request.GET.get('sort', default), 'date')

@paginate
@searchable
@sortable
@handlesubdomain
def index(request):
	request.context['sort_method'] = jackSortMethod(request, 'popular')

	request.context['jack_list'] = Jack.objects.with_details(
		page=request.context['current_page'],
		sort=request.context['sort_method'],
		homepage=True,
		perspective=request.session['user_id'] if 'user_id' in request.session \
				else getIp(request),
		perspective_ip=False if 'user_id' in request.session else True)

	if len(request.context['jack_list']) < djangosettings.JACKS_PER_PAGE:
		request.context['page_next'] = False

	print(Jack.objects.count())
	print((request.context['current_page']  - 1) * djangosettings.JACKS_PER_PAGE)

	return render(request, 'index.html', request.context)

@communitypage
def about(request):
	return render(request, 'about.html', request.context)

def stats(request):
	graph = request.GET.get('graph', None)
	if graph is not None:
		return HttpResponse(bar.to_json())

	context = {
	}
	return render(request, 'stats.html', context)

def calendarGraph(request):
	year = timedelta(days=365)
	day = timedelta(days=1)

	dateTo = request.GET.get('to', None)
	if dateTo is None:
		dateTo = date.today()
	else:
		dateTo = datetime.strptime(dateTo, '%Y-%m-%d').date()

	dateFrom = request.GET.get('from', None)
	if dateFrom is None:
		dateFrom = dateTo - year
	else:
		dateFrom = datetime.strptime(dateFrom, '%Y-%m-%d').date()

	user = request.GET.get('user', request.session.get('user_name', None))
	if user is None:
		return HttpResponse('no user provided')

	jackData = Jack.objects.filter(user__name=user)

	jacksPerDay = {}

	for jack in jackData:
		jackDate = jack.date.date()
		if jackDate in jacksPerDay:
			jacksPerDay[jackDate] += 1
		else:
			jacksPerDay[jackDate] = 1

	jacksPerDayLow = min(jacksPerDay.values())
	jacksPerDayHigh = max(jacksPerDay.values())

	months = []

	days = []
	currentDate = dateFrom
	currentWeek = 0
	timeInMonth = 0

	while currentDate <= dateTo:
		weekday = currentDate.isoweekday() % 7

		if weekday == 0:
			currentWeek += 1

		highColor = 16
		lowColor = 128

		dayColor = jacksPerDay.get(currentDate, None)
		if dayColor is None:
			dayColor = 216
		else:
			#dayColor = int(256 - dayColor * (256 / jacksPerDayHigh))
			print(dayColor)
			dayColor = int((lowColor - highColor) - ((jacksPerDayLow * dayColor) / jacksPerDayHigh) * (lowColor - highColor)) + highColor
			print(dayColor)

		days.append((
			(currentWeek * 12) + 16,
			(weekday * 12) + 16,

			#coloring
			dayColor,
			dayColor,
			dayColor
		))

		if len(months) <= 0 or months[-1][3] != currentDate.month:
			timeInMonth += 1
			if timeInMonth > 14:
				timeInMonth = 0
				months.append((
					days[-1][0],
					12,
					currentDate.strftime('%b').lower(),
					currentDate.month
				))

		currentDate += day

	dayNames = [
		#(0, 0, 'S'),
		(0, 37, 'M'),
		#(0, 40, 'T'),
		(0, 61, 'W'),
		#(0, 80, 'T'),
		(0, 85, 'F'),
		#(0, 120, 'S')
	]

	context = {
		'daynames': dayNames,
		'months': months,
		'days': days,
		'height': 100,
		'width': int(len(days) / 7) * 12 + 48
	}
	return render(request, 'graphs/calendar.svg', context, content_type='image/svg+xml')

@communitypage
def community(request):
	return render(request, 'community.html', request.context)

@communitypage
@paginate
def tags(request):
	splitUrl = request.META['PATH_INFO'].split('/')
	if len(splitUrl) >= 2 and splitUrl[2] != '':
		return HttpResponseRedirect('/search/tag:' + splitUrl[2])

	request.context['tag_list']  = Tag.objects \
		.annotate(occurrences=Count('jack_tags')) \
		.order_by('-occurrences') \
		[
			(request.context['current_page'] - 1) * djangosettings.TAGS_PER_PAGE:
			request.context['current_page'] * djangosettings.TAGS_PER_PAGE
		]

	if request.context['tag_list'].count() < djangosettings.TAGS_PER_PAGE:
		request.context['page_next'] = False

	return render(request, 'popular_tags.html', request.context)

@communitypage
def leader_board(request):
	return render(request, 'leader_board.html', request.context)

@communitypage
def developer(request):
	return render(request, 'developer.html', request.context)

@handlesubdomain
def bros(request):
	context = {
	}
	return render(request, 'bros.html', context)

def customize(request):
	context = {
	}
	return render(request, 'customize.html', context)

@communitypage
def app_download(request):
	return render(request, 'app_download.html', request.context)

def promo(request):
	context = {
	}
	return render(request, 'promo.html', context)

@paginate
def search(request):
	searchTerm = request.GET.get('term', '').split(' ')
	urlTerm = request.META['PATH_INFO'].split('/')[2:]

	context = {
		'is_searchable': True,
		'is_search_page': True,
		'is_sortable': True,
		'sort_method': jackSortMethod(request, 'popular'),
		'search_query': ' '.join(searchTerm),
		'search_source_labels': '/'.join(urlTerm),
		'search_tag_list': [],
		'search_user_list': []
	}

	if searchTerm == [''] and urlTerm == ['']:
		context['empty_search_query'] = True
		return render(request, 'search.html', context)

	searchTags = []
	searchUsers = []
	searchWords = []

	for term in urlTerm:
		term = term.replace('+', ' ')
		if term.startswith('tag:'):
			tag = term.replace('tag:','')
			searchTags.append(tag)
			context['search_tag_list'].append(tag)
		elif term.startswith('user:'):
			user = term.replace('user:','')
			searchUsers.append(user)
			context['search_user_list'].append(user)
		else:
			searchWords.append(term)

	for term in searchTerm:
		term = term.replace('+', ' ')
		if term.startswith('tag:'):
			searchTags.append(term.replace('tag:',''))
		elif term.startswith('user:'):
			searchUsers.append(term.replace('user:',''))
		else:
			searchWords.append(term)

	foundJacks = Jack.objects

	jackFilterWords = None
	for word in searchWords:
		newFilter = Q(comment__icontains=word)
		jackFilterWords = newFilter if jackFilterWords is None \
			else jackFilterWords & newFilter

	jackFilterTags = None
	for tag in searchTags:
		newFilter = Q(tags__text__iexact=tag)
		jackFilterTags = newFilter if jackFilterTags is None \
			else jackFilterTags | newFilter

	jackFilterUser = None
	for user in searchUsers:
		newFilter = Q(user__name__iexact=user)
		jackFilterUser = newFilter if jackFilterUser is None \
			else jackFilterUser | newFilter

	if jackFilterWords is not None:
		foundJacks = foundJacks.filter(jackFilterWords)

	if jackFilterTags is not None:
		foundJacks = foundJacks.filter(jackFilterTags)

	if jackFilterUser is not None:
		foundJacks = foundJacks.filter(jackFilterUser)

	if foundJacks.count() <= 0:
		return render(request, 'search.html', context)

	foundJacks = Jack.objects.with_details(
		page=request.context['current_page'],
		sort=context['sort_method'],
		perspective=request.session['user_id'] if 'user_id' in request.session \
				else getIp(request),
		perspective_ip=False if 'user_id' in request.session else True,
		jack_id=list(foundJacks.values_list('id', flat=True)))

	context['page_next'] = request.context['page_next'] \
			if len(foundJacks) >= djangosettings.JACKS_PER_PAGE else False
	context['page_prev'] = request.context['page_prev']

	context['results'] = foundJacks

	return render(request, 'search.html', context)

def search_suggestion(request):

	#i'm fully aware of how inefficient this is but... i don't like orm nor do i
	#want to break out into full on sql
	suggestedTags = Tag.objects \
		.filter(text__icontains=request.GET.get('term')) \
		.values_list('text', flat=True)[0:5]

	suggestedUsers = User.objects \
		.filter(name__icontains=request.GET.get('term')) \
		.values_list('name', flat=True)[0:5]

	suggestedTags = [{'type': 'tag', 'text': tag} for tag in suggestedTags]
	suggestedUsers = [{'type': 'user', 'text': user} for user in suggestedUsers]

	fullList = suggestedTags + suggestedUsers
	fullList = sorted(fullList, key=lambda item: item['text'].lower())

	suggestedTagsJson = json.dumps(fullList)

	return HttpResponse(suggestedTagsJson)

def tag_suggestion(request):

	#could use more personal data, this will work for now
	suggestedTags = Tag.objects \
		.filter(text__icontains=request.GET.get('term')) \
		.values_list('text', flat=True)[0:5]

	suggestedTagsJson = json.dumps(list(suggestedTags))

	return HttpResponse(suggestedTagsJson)

def bro_suggestion(request):

	suggestedBros = User.objects \
		.filter(name__icontains=request.GET.get('term')) \
		.values_list('name', flat=True)[0:5]

	suggestedTagsJson = json.dumps(list(suggestedBros))

	return HttpResponse(suggestedTagsJson)

def api(request):
	json.dumps()
	return HttpResponse(jsonResponse)

def standalone_jack(request):
	#the id should be whatever is directly after /jack/
	jackUrlId = request.META['PATH_INFO'].split('/')[2:][0]
	jackId = int(jackUrlId)

	jackObject = Jack.objects.with_details(
		perspective=request.session['user_id'] if 'user_id' in request.session \
				else getIp(request),
		perspective_ip=False if 'user_id' in request.session else True,
		jack_id=jackId)

	if len(list(jackObject)) == 0:
		raise Http404("This jack doesn't exist")

	jackObject = jackObject[0]

	context = {
		'jack': jackObject,
		'standalone': True
	}

	return render(request, 'standalone_jack.html', context)

def modifyjack(request):
	jackObject = Jack.objects.filter(id = request.POST['jack_id']) \
		.select_related('user').first()

	#verify ownership before doing anything with the post
	if not jackObject.user.id == request.session['user_id']:
		raise Exception('nice try')

	if request.POST['operation'] == 'visibility':
		jackObject.private = not jackObject.private
		jackObject.save()

	elif request.POST['operation'] == 'edit':
		context = {
			'jack': Jack.objects.with_details(jack_id=jackObject.id)[0],
			'comment_filler': jackObject.comment,
			'return_location': request.POST['return_location']
		}
		return render(request, 'modify_jack.html', context)

	elif request.POST['operation'] == 'delete':
		jackObject.delete()

	elif request.POST['operation'] == 'submit_edit':
		print(request.POST['new_jack'])
		jackObject.comment = request.POST['new_jack']
		jackObject.save()

	return HttpResponseRedirect(request.POST['return_location'])

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
		voteObject.date = datetime.today()
		voteObject.points = userChoice
		voteObject.save()

		replyObject = [{
			'jack': jackObject.id,
			'votes': jackObject.votes()
		}]
		return HttpResponse(json.dumps(replyObject))

	else:
		voteObjects = Vote.objects.filter(
			jack=jackObject,
			ip=getUserIp(request),
			user__isnull=True)

		if voteObjects.count() >= 1:
			voteObject = voteObjects.first()
		else:
			voteObject = Vote(
				ip=getUserIp(request),
				jack=jackObject)

		voteObject.date = datetime.today()
		voteObject.points = userChoice
		voteObject.save()

		replyObject = [{
			'jack': jackObject.id,
			'votes': jackObject.votes()
		}]
		return HttpResponse(json.dumps(replyObject))

def settings(request):
	if not 'user_logged_in' in request.session:
		return HttpResponseRedirect('/dash/')

	userObject = User.objects.get(
		id = request.session['user_id'])
	userSettings = userObject.settings

	user_options = {
		'private': userSettings.private,
		'show_on_home_page': userSettings.on_homepage,
		'show_date': userSettings.show_date,
		'show_time': userSettings.show_time,
	}

	context = {
		'options': user_options
	}

	return render(request, 'settings.html', context)

def submit_settings(request):
	if request.method != 'POST':
		return HttpResponseRedirect('/dash/')

	if not 'user_logged_in' in request.session:
		return HttpResponseRedirect('/dash/')

	userObject = User.objects.get(
		id = request.session['user_id'])

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
	context = { }

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
	captchaRequest.add_header(
			"Content-Type","application/x-www-form-urlencoded;charset=utf-8")

	captchaResponse = ''
	with urllib.request.urlopen(captchaRequest, encodedPostData) as f:
		captchaResponse += f.read().decode('utf-8')

	decodedCaptchaResponse = json.loads(captchaResponse)
	if not decodedCaptchaResponse['success']:
		raise Exception('must verify captcha')

def signup(request):
	context = { }

	if request.method == 'POST':
		username = str(request.POST.get('username', ''))
		password = str(request.POST.get('password', ''))
		private = str(request.POST.get('private', ''))

		try:
			captchaClientResponse = str(request.POST.get(
				'g-recaptcha-response', ''))

			#get the users ip
			x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
			if x_forwarded_for:
				ip = x_forwarded_for.split(',')[0]
			else:
				ip = request.META.get('REMOTE_ADDR')

			verifyCaptcha(captchaClientResponse, ip)

			createUser(username, password, private == 'on')
			signin(request)
			return HttpResponseRedirect('/dash')
		except Exception as e:
			context['error'] = e.args[0]

	return render(request, 'signup_standalone.html', context)

def feed(request):
	isUser = False
	isPrivate = False
	userJackList = False
	hasJacked = False
	subdomain = getSubdomain(request.META['HTTP_HOST'])

	userObject = User.objects.get(name__iexact = subdomain)

	isUser = True

	isPrivate = userObject.settings.private

	context = {
		'sort_method': jackSortMethod(request, 'new')
	}

	if not isPrivate:
		pageNumber = request.GET.get('page', 1)
		try:
			pageNumber = int(pageNumber)
		except:
			pageNumber = 1

		userJackList = Jack.objects.with_details(
			page=pageNumber,
			sort=context['sort_method'],
			user=userObject.id,
			perspective=request.session.get('user_id'))

		context['page_next'] = pageNumber + 1 if  len(list(userJackList)) >= djangosettings.JACKS_PER_PAGE else False
		context['page_prev'] = pageNumber - 1 if pageNumber > 1 else False

		if len(list(userJackList)) > 0:
			day = timedelta(days=1)
			hasJacked = datetime.now(timezone.utc) - userJackList[0].date < day

	if hasJacked:
		jacked_message = YesWords.objects.random_word('yes')
	else:
		jacked_message = YesWords.objects.random_word('no')

	context['jack_list'] = userJackList
	context['search_source_labels'] = 'user:' + userObject.name
	context['username'] = subdomain
	context['title_text_a'] = jacked_message
	context['is_user'] = isUser
	context['is_private'] = isPrivate
	context['is_searchable'] = not isPrivate
	context['is_sortable'] = not isPrivate

	return render(request, 'feed.html', context)

def dash(request):
	#dash is basically useless if you're not logged in, so instead of throwing
	#errors or something, it's easier if we just redirect to the front page
	if not 'user_logged_in' in request.session:
		return HttpResponseRedirect('/')

	context = {
		'comment_filler': YesWords.objects.random_word('yes'),
		'filler_user': User.objects.order_by('?')[:3],
		'is_searchable': True,
		'is_sortable': True,
		'sort_method': jackSortMethod(request, 'new'),
		'search_source_labels': 'user:' + request.session['user_name']
	}

	pageNumber = request.GET.get('page', 1)
	try:
		pageNumber = int(pageNumber)
	except:
		pageNumber = 1

	jackList = Jack.objects.with_details(
		page=pageNumber,
		sort=context['sort_method'],
		user=request.session['user_id'],
		perspective=request.session['user_id'])

	context['page_next'] = pageNumber + 1 if  len(list(jackList)) >= djangosettings.JACKS_PER_PAGE else False
	context['page_prev'] = pageNumber - 1 if pageNumber > 1 else False

	context['jack_list'] = jackList

	return render(request, 'dash.html', context)

#if multiple parts of the application need the user's ip object, this prevents
#multiple database querys
userIpObject = None
def getUserIp(request):
	global userIpObject
	if userIpObject is not None:
		return userIpObject

	#if an ip alread exists, no need to create another entry for it
	userIpObject, created = Ip.objects.get_or_create(address=getIp(request))

	return userIpObject

def getIp(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		clientIp = x_forwarded_for.split(',')[0]
	else:
		clientIp = request.META.get('REMOTE_ADDR')

	return clientIp

def submit_jack(request):
	if request.method != 'POST':
		return HttpResponseRedirect('/dash/')

	finished = True
	userObject = User.objects.get(id = request.session['user_id'])
	jackStartTime = userObject.started
	userObject.started = None

	if 'new_jack' in request.POST and request.POST['new_jack'] != '':
		message = str(request.POST.get('new_jack', ''))
	elif 'start_time' in request.POST:
		userObject.started = datetime.today()
		userObject.save()
		return HttpResponseRedirect('/dash/')
	elif 'no_finish' in request.POST:
		message = None
		finished = False
	else:
		return HttpResponseRedirect('/dash/')

	userObject.save()

	userIp = getUserIp(request)

	newJack = Jack(
		user=userObject,
		comment=message,
		date=datetime.today(),
		ip=userIp,
		finished=finished,
		start=jackStartTime)

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
		filename += '.' + str(uri.mimetype.split('/')[-1])

		newImage.data.save(filename, File(imageFile))
		newImage.save()
		newJack.image = newImage

	if 'jack_link_url' in request.POST \
			and not request.POST['jack_link_url'] == '':
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

	if 'jack_tag' in request.POST and not request.POST['jack_tag'] == '':
		tagStrings = request.POST['jack_tag'].split(",")
		tagStrings = [s.strip(' ') for s in tagStrings]

		for tagText in tagStrings:
			userTagObject, created = Tag.objects.get_or_create(text=tagText)
			newJack.tags.add(userTagObject)

	return HttpResponseRedirect('/dash/')

def getSubdomain(url):
	splitUrl = url.split('.')

	urlParts = len(splitUrl)

	if urlParts >= 3:
		return splitUrl[0]

	return False

#returns True if a use with username exists, otherwise returns false
def userExists(username):
	return False if User.objects.filter(name__iexact = username).count() == 0 \
			else True

#creates user or raises exception detailing what went wrong
def createUser(username, password, isPrivate=False):
	if username == '':
		raise Exception('must supply a username')
	if not username.isalnum():
		raise Exception('username must be alphanumeric')
	if userExists(username):
		raise Exception('username already exists')

	hash_salt = createPasswordSalt()
	hashed_password = hashPassword(password, hash_salt)

	newUserSettings = UserSettings()
	newUserSettings.private = isPrivate
	newUserSettings.save()

	newUser = User(
		name=username,
		password_hash=hashed_password,
		last_online=datetime.today(),
		creation_date=datetime.today(),
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
