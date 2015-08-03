from django.db import models
from django.db.models import Sum

class UserSubmitted(models.Model):
	user = models.ForeignKey('User', null=True)
	ip = models.ForeignKey('Ip')
	private = models.BooleanField(default=False)
	hidden = models.BooleanField(default=False)

class User(models.Model):
	name = models.CharField(max_length=16)
	password_hash = models.CharField(max_length=128)
	password_salt = models.CharField(max_length=32)
	last_online = models.DateTimeField()
	creation_date = models.DateTimeField()
	settings = models.OneToOneField('UserSettings')
	#ips = models.ManyToManyField('Ip')

class UserSettings(models.Model):
	private = models.BooleanField(default=False)
	on_homepage = models.BooleanField(default=True)
	show_date = models.BooleanField(default=True)
	show_time = models.BooleanField(default=True)

class Jack(UserSubmitted):
	date = models.DateTimeField()
	comment = models.CharField(max_length=160)
	location = models.ForeignKey('Geolocation', null=True)
	link = models.ForeignKey('Link', null=True)
	image = models.ForeignKey('Image', null=True)
	bros = models.ManyToManyField('User', related_name='jack_bros')

	def votes(self):
		votesum = self.vote_set.all().aggregate(Sum('points'))['points__sum']
		return 0 if votesum is None else votesum

class Vote(UserSubmitted):
	jack = models.ForeignKey('Jack')
	date = models.DateTimeField()
	points = models.IntegerField()

class Ip(models.Model):
	address = models.CharField(max_length=24)

class Geolocation(UserSubmitted):
	lat = models.DecimalField(max_digits=11, decimal_places=8)
	lng = models.DecimalField(max_digits=11, decimal_places=8)

class Link(UserSubmitted):
	url = models.CharField(max_length=512)

class Image(UserSubmitted):
	data = models.ImageField(upload_to='.', default = 'media/none.png')

	SOURCES = (('f', 'file'), ('c', 'camera'))
	source = models.CharField(max_length='1', choices=SOURCES, default='f')

#this is just the different' words to show, these models shouldn't be edited
class YesWords(models.Model):
	word = models.CharField(max_length=32)

	def save(self, *args, **kwargs):
		pass
	def delete(self):
		pass

class NoWords(models.Model):
	word = models.CharField(max_length=32)

	def save(self, *args, **kwargs):
		pass
	def delete(self):
		pass
