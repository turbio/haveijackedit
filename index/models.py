from django.db import models

class user(models.Model):
	name = models.CharField(max_length=16)
	password_hash = models.CharField(max_length=128)
	password_salt = models.CharField(max_length=32)
	last_online = models.DateTimeField()
	creation_date = models.DateTimeField()

class jack(models.Model):
	user_id = models.ForeignKey(user)
	date = models.DateTimeField()
	comment = models.CharField(max_length=160)

class geolocation(models.Model):
	jack = models.ForeignKey(jack)
	lat = models.DecimalField(max_digits=11, decimal_places=8)
	lng = models.DecimalField(max_digits=11, decimal_places=8)

class link(models.Model):
	jack = models.ForeignKey(jack)
	url = models.CharField(max_length=2083)

class image(models.Model):
	jack = models.ForeignKey(jack)
	path = models.CharField(max_length=2083)

class jack_bro(models.Model):
	jack = models.ForeignKey(jack)
	bro = models.ForeignKey(user)

class yes_word(models.Model):
	word = models.CharField(max_length=32)

class no_word(models.Model):
	word = models.CharField(max_length=32)
