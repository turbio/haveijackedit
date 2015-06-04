from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from .models import jack, user
import hashlib
import time
import datetime

# Create your views here.
def index(request):
	if request.method == 'POST':
		try:
			handleUsercredentials(request)
		except:
			return HttpResponse("you did something wrong (probably)")

	latest_jack = jack.objects.order_by('date')[0]
	template = loader.get_template('index/index.html')
	context = {'latest_jack': latest_jack}
	return render(request, 'index/index.html', context)

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
		pass

def signin(username, password):
	pass

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
