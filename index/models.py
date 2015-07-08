from django.db import models

class user(models.Model):
	name = models.CharField(max_length=16)
	password_hash = models.CharField(max_length=128)
	password_salt = models.CharField(max_length=32)
	last_online = models.DateTimeField()
	creation_date = models.DateTimeField()
	settings = models.ForeignKey('user_settings')

class user_settings(models.Model):
	private = models.BooleanField(default=False)
	on_homepage = models.BooleanField(default=True)
	show_data = models.BooleanField(default=True)
	show_time = models.BooleanField(default=True)

class jack(models.Model):
	user_id = models.ForeignKey(user)
	date = models.DateTimeField()
	comment = models.CharField(max_length=160)

class geolocation(models.Model):
	jack = models.ForeignKey('jack')
	lat = models.DecimalField(max_digits=11, decimal_places=8)
	lng = models.DecimalField(max_digits=11, decimal_places=8)

class link(models.Model):
	jack = models.ForeignKey('jack')
	url = models.CharField(max_length=512)
	#scheme = models.CharField(max_length=8)
	#host = models.CharField(max_length=255)
	#path = models.CharField(max_length=256)

class image(models.Model):
	jack = models.ForeignKey('jack')
	data = models.ImageField(upload_to='./data/jack_image/')
	data = models.CharField(max_length=50000)

class jack_bro(models.Model):
	jack = models.ForeignKey('jack')
	bro = models.ForeignKey(user)

class yes_word(models.Model):
	word = models.CharField(max_length=32)

class no_word(models.Model):
	word = models.CharField(max_length=32)
