from django.db import models

# Create your models here.
class user(models.Model):
	name = models.CharField(max_length=16)
	password_hash = models.CharField(max_length=512)
	password_salt = models.CharField(max_length=32)
	last_online = models.DateTimeField('date published')
	creation_date = models.DateTimeField('date published')


class jack(models.Model):
	user_id = models.ForeignKey(user)
	date = models.DateTimeField('date published')
	comment = models.CharField(max_length=160)
