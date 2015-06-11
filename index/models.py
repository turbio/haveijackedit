from django.db import models

# Create your models here.
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

class yes_word(models.Model):
	word = models.CharField(max_length=32)
