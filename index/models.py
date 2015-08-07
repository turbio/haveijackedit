from django.db import models
from django.db.models import Sum, F, When, Case, Value, CharField, Q

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

class UserSettings(models.Model):
	private = models.BooleanField(default=False)
	on_homepage = models.BooleanField(default=True)
	show_date = models.BooleanField(default=True)
	show_time = models.BooleanField(default=True)

class JackManager(models.Manager):
	def with_details(self):
		#return self.order_by('date').reverse() \
			#.select_related('image', 'link', 'location', 'user', 'ip') \
			#.prefetch_related('bros', 'vote', 'vote__user') \
			#.annotate(votes=Sum('vote__points'))

		q = open('./index/jack_detail.sql', 'r').read()
		print(q)
		return self.raw(q)

class Jack(UserSubmitted):
	date = models.DateTimeField()
	comment = models.CharField(max_length=160)
	location = models.ForeignKey('Geolocation', null=True)
	link = models.ForeignKey('Link', null=True)
	image = models.ForeignKey('Image', null=True)
	bros = models.ManyToManyField('User', related_name='jack_bros')
	objects = JackManager()

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
class RandomWordManager(models.Manager):
	def random_word(self, default=None):
		word = self.order_by('?').first()
		if word is not None:
			word = word.word
		elif default is not None:
			word = default
		else:
			word = None

		return word


class YesWords(models.Model):
	word = models.CharField(max_length=32)
	objects = RandomWordManager()

	def save(self, *args, **kwargs):
		pass
	def delete(self):
		pass

class NoWords(models.Model):
	word = models.CharField(max_length=32)
	objects = RandomWordManager()

	def save(self, *args, **kwargs):
		pass
	def delete(self):
		pass
