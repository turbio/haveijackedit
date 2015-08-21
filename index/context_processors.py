from django.conf import settings

def const_settings(request):
	print('lmao')
	return {
		'HOST_NAME': settings.HOST_NAME,
		'MEDIA_URL': settings.MEDIA_URL
	}
