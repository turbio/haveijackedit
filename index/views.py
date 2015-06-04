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
		username = request.POST.get("username", "")
		if not username.isalnum():
			return HttpResponse('wow, nice username, to bad it\'s not alphanumeric')

		hash_salt = hashlib.md5(str(time.time()).encode()).hexdigest()
		hashed_password = hashlib.sha512(request.POST.get("password", "").encode()).hexdigest()

		newUser = user(
			name=username,
			password_hash=hashed_password,
			last_online=datetime.datetime.today(),
			creation_date=datetime.datetime.today(),
			password_salt=hash_salt)
		newUser.save()
		return HttpResponse("all is well")
		#return HttpResponse("yep" + str(request.POST.get("password", "")) + ";")
	else:
		latest_jack = jack.objects.order_by('date')[0]
		template = loader.get_template('index/index.html')
		context = {'latest_jack': latest_jack}
		return render(request, 'index/index.html', context)
