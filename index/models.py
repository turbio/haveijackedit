from django.db import models
from django.conf import settings as djangosettings
from django.db.models import Sum, Count, F, When, Case, Value, CharField, Q
from django.db.models.functions import Concat
from datetime import datetime, timezone
import re

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
	profile = models.OneToOneField('UserProfile')
	started = models.DateTimeField(null=True)
	flairs = models.ManyToManyField('Flair', through='FlairRelationship')

	def score(self):
		return User.objects.raw(
			open("index/user_score.sql").read() % self.id)[0].score

	def isJacking(self):
		return self.started is not None

	def jackTime(self):
		if self.started is not None:
			return datetime.now(timezone.utc) - self.started
		else:
			return None

	def jackTimeFormated(self):
		diff = self.jackTime()
		if diff is None:
			return None

		formated = {"days": diff.days}
		formated["hours"], rem = divmod(diff.seconds, 3600)
		formated["minutes"], formated["seconds"] = divmod(rem, 60)

		return formated

class FlairRelationship(models.Model):
	user = models.ForeignKey(User)
	flair = models.ForeignKey('Flair')
	active = models.BooleanField(default=True)

class Flair(models.Model):
	name = models.CharField(max_length=16)
	image = models.CharField(max_length=128)

class UserProfile(models.Model):
	bio = models.CharField(null=True)
	url = models.CharField(null=True)
	kinks = models.ManyToManyField('Tag', related_name='user_kinks')

class UserSettings(models.Model):
	private = models.BooleanField(default=False)
	hidden = models.BooleanField(default=False)
	on_homepage = models.BooleanField(default=True)
	show_date = models.BooleanField(default=True)
	show_time = models.BooleanField(default=True)

class JackManager(models.Manager):
	#adds a lot of details to jacks
	#user: to only show jacks by a single user id or ip address
	#perspective: show from a particular user id or ip address' perspective
	#sort: a string determining how to sort jacks, values:
	#"votes": sort by the number of votes recieved
	#"score": sort by the score
	#"date": sort by date
	#limit: number of posts to show
	#page: which page to return, assuming that limit determines the page length
	#homepage: only show jacks that would normally appear on homepage
	#perspective_ip: if the perspective is an ip or user id
	#jack_id: only show this specific jack
	def with_details(
			self,
			user=None,
			perspective=None,
			sort=False,
			limit=djangosettings.JACKS_PER_PAGE,
			page=1,
			homepage=False,
			perspective_ip=False,
			jack_id=None):

		baseQuery = """
SELECT
	index_jack.usersubmitted_ptr_id,
	index_jack.comment AS comment,
	index_jack.finished AS finished,
	IFNULL(SUM(index_vote.points), 0) AS votes,
	index_user.name AS user_name,
	index_ip.address AS ip_address,
	index_geolocation.lat AS location_lat,
	index_geolocation.lng AS location_lng,
	index_link.url AS url,
	index_image.data AS image_file,
	index_image.source AS image_source,
	visibility.private AS private,
	TIMESTAMPDIFF(DAY,index_jack.start,index_jack.date) AS duration_day,
	MOD(TIMESTAMPDIFF(HOUR,index_jack.start,index_jack.date), 24) AS duration_hour,
	MOD(TIMESTAMPDIFF(MINUTE,index_jack.start,index_jack.date), 60) AS duration_minute,
	MOD(TIMESTAMPDIFF(SECOND,index_jack.start,index_jack.date), 60) AS duration_second,
	TIMESTAMPDIFF(SECOND,index_jack.start,index_jack.date) AS duration,
	CASE
	WHEN TIMESTAMPDIFF(SECOND,index_jack.date,UTC_TIMESTAMP()) < 60
		THEN CONCAT(TIMESTAMPDIFF(SECOND,index_jack.date,UTC_TIMESTAMP())," seconds ago")
	WHEN TIMESTAMPDIFF(MINUTE,index_jack.date,UTC_TIMESTAMP()) < 60
		THEN CONCAT(TIMESTAMPDIFF(MINUTE,index_jack.date,UTC_TIMESTAMP())," minutes ago")
	WHEN TIMESTAMPDIFF(HOUR,index_jack.date,UTC_TIMESTAMP()) < 60
		THEN CONCAT(TIMESTAMPDIFF(HOUR,index_jack.date,UTC_TIMESTAMP())," hours ago") ELSE CONCAT(TIMESTAMPDIFF(DAY,index_jack.date,UTC_TIMESTAMP())," days ago")
	END AS age,
	(
		SELECT
			GROUP_CONCAT(index_tag.text SEPARATOR ',')
		FROM
			index_jack_tags
		INNER JOIN index_tag ON
			index_jack_tags.tag_id = index_tag.id
		WHERE index_jack_tags.jack_id = index_jack.usersubmitted_ptr_id
	) AS tag,
	(
		SELECT
			GROUP_CONCAT(index_user.name SEPARATOR ',')
		FROM
			index_jack_bros
		INNER JOIN index_user ON
			index_jack_bros.user_id = index_user.id
		WHERE index_jack_bros.jack_id = index_jack.usersubmitted_ptr_id
	) AS bro
	%s %s %s
FROM
	index_jack
LEFT OUTER JOIN index_vote ON
	( index_jack.usersubmitted_ptr_id = index_vote.jack_id )
LEFT JOIN
	(
		SELECT
			((index_usersettings.private) OR (index_usersubmitted.private)) AS private,
			(index_usersettings.hidden OR index_usersubmitted.hidden) AS hidden,
			index_usersettings.on_homepage AS on_homepage,
			index_jack.usersubmitted_ptr_id AS jack_id
		FROM
			index_jack
		INNER JOIN index_usersubmitted ON
			index_jack.usersubmitted_ptr_id = index_usersubmitted.id
		INNER JOIN index_user ON
			index_user.id = index_usersubmitted.user_id
		INNER JOIN index_usersettings ON
			index_usersettings.id = index_user.settings_id
	) AS visibility
	ON visibility.jack_id = index_jack.usersubmitted_ptr_id
INNER JOIN index_usersubmitted ON
	( index_jack.usersubmitted_ptr_id = index_usersubmitted.id )
LEFT OUTER JOIN index_user ON
	( index_usersubmitted.user_id = index_user.id )
INNER JOIN index_ip ON
	( index_usersubmitted.ip_id = index_ip.id )
LEFT OUTER JOIN index_geolocation ON
	( index_jack.location_id = index_geolocation.usersubmitted_ptr_id )
LEFT OUTER JOIN index_link ON
	( index_jack.link_id = index_link.usersubmitted_ptr_id )
LEFT OUTER JOIN index_image ON
	( index_jack.image_id = index_image.usersubmitted_ptr_id )
WHERE
	(NOT visibility.private OR index_user.id = "%s")
	AND (NOT visibility.hidden)
	AND index_jack.finished %s %s %s
GROUP BY
	index_jack.usersubmitted_ptr_id
ORDER BY %s LIMIT %s OFFSET %s"""

		ownerQuery = """,CASE WHEN index_user.id = "%s" THEN 1 ELSE 0 END AS isowner""" % perspective
		voteDirectionQuery = """,(SELECT index_vote.points FROM index_vote INNER JOIN index_usersubmitted ON index_vote.usersubmitted_ptr_id = index_usersubmitted.id LEFT JOIN index_user ON index_usersubmitted.user_id = index_user.id INNER JOIN index_ip ON index_usersubmitted.ip_id = index_ip.id WHERE (index_vote.jack_id = index_jack.usersubmitted_ptr_id) AND %s) AS vote_direction""" % ( ("""(index_ip.address = "%s") AND (index_usersubmitted.user_id IS NULL)""" % perspective) if perspective_ip else ("""(index_usersubmitted.user_id = "%s")""" % perspective))
		scoreQuery = """,( 100 + ((CHAR_LENGTH(index_jack.comment) / 160) * 200) - (POW(TIMESTAMPDIFF(SECOND,index_jack.date,UTC_TIMESTAMP()) / (60 * 60), 2) * 2) + (CASE WHEN IFNULL(SUM(index_vote.points), 0) > 0 THEN POW(IFNULL(SUM(index_vote.points), 0), 2) * 100 ELSE IFNULL(SUM(index_vote.points), 0) * 100 END) ) AS score"""

		orderDateQuery = """index_jack.date DESC"""
		orderScoreQuery = """score DESC"""
		orderTopQuery = """votes DESC"""

		orderQuery = orderDateQuery

		if sort is "votes":
			orderQuery = orderTopQuery
		elif sort is "score":
			orderQuery = orderScoreQuery

		homepageQuery = """AND visibility.on_homepage"""
		singleUserQuery = """AND index_user.id = "%s" """ % user

		if jack_id is not None:
			if type(jack_id) is int:
				specificJackQuery = """AND index_jack.usersubmitted_ptr_id = "%s" """ % jack_id
			elif type(jack_id) is list:
				#sqlUserArray = str(tuple([int(uid) for uid in jack_id]))
				sqlUserArray = '(' + ','.join(str(uid) for uid in jack_id) + ')'
				specificJackQuery = """AND index_jack.usersubmitted_ptr_id IN %s """ % sqlUserArray

		query = baseQuery % (
				ownerQuery if perspective is not None else "",
				voteDirectionQuery if perspective is not None else "",
				scoreQuery,
				perspective if perspective is not None else "",
				homepageQuery if homepage else "",
				singleUserQuery if user is not None else "",
				specificJackQuery if jack_id is not None else "",
				orderQuery,
				limit,
				int((page - 1) * limit)
			)

		queryResults = list(self.raw(query))

		for i in range(len(queryResults)):
			if queryResults[i].bro is not None:
				queryResults[i].bro  = queryResults[i].bro.lstrip(',').split(',')

			if queryResults[i].tag is not None:
				queryResults[i].tag  = queryResults[i].tag.lstrip(',').split(',')

		return queryResults

class Jack(UserSubmitted):
	date = models.DateTimeField()
	comment = models.CharField(max_length=160, null=True)
	location = models.ForeignKey('Geolocation', null=True)
	link = models.ForeignKey('Link', null=True)
	image = models.ForeignKey('Image', null=True)
	bros = models.ManyToManyField('User', related_name='jack_bros')
	tags = models.ManyToManyField('Tag', related_name='jack_tags')
	start = models.DateTimeField(null=True)
	objects = JackManager()
	finished = models.BooleanField()

	def votes(self):
		votesum = self.vote_set.all().aggregate(Sum('points'))['points__sum']
		return 0 if votesum is None else votesum

	def friendly_url(self):
		pattern = re.compile('[\W]+')
		return pattern.sub('_', self.comment)

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

class Tag(models.Model):
	text = models.CharField(max_length=32)

class Promo(models.Model):
	description = models.CharField(max_length=512)
	code = models.CharField(max_length=16)
	start = models.DateTimeField(null=True)
	end = models.DateTimeField(null=True)
	uses = models.IntegerField(null=True)
	redirect = models.CharField(max_length=16)

	#only flairs for now
	flair = models.ForeignKey('Flair', null=True)

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
