from django.conf import settings
from .models import User

def const_settings(request):
	return {
		'HOST_NAME': settings.HOST_NAME,
		'MEDIA_URL': settings.MEDIA_URL
	}

def user_object(request):
	return {
		'user': User.objects.filter(id=request.session.get('user_id')).first()
	}
