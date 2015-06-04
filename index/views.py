from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from .models import jack, user

# Create your views here.
def index(request):
	latest_jack = jack.objects.order_by('date')[0]
	template = loader.get_template('index/index.html')
	context = {'latest_jack': latest_jack}
	return render(request, 'index/index.html', context)
