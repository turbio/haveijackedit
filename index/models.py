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
	hidden = models.BooleanField(default=False)
	on_homepage = models.BooleanField(default=True)
	show_date = models.BooleanField(default=True)
	show_time = models.BooleanField(default=True)

class JackManager(models.Manager):
	def with_details(self, user=None, perspective=None, score=False, limit=25):
		print("lmao: " + str([user, perspective, score, limit]))

		baseQuery = """
SELECT
	index_jack.usersubmitted_ptr_id,
	index_jack.comment AS comment,
	IFNULL(SUM(index_vote.points), 0) AS votes,
	index_user.name AS user_name,
	index_ip.address AS ip_address,
	index_geolocation.lat AS location_lat,
	index_geolocation.lng AS location_lng,
	index_link.url AS url,
	index_image.data AS image_file,
	index_image.source AS image_source,
	visibility.private AS private,
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
			GROUP_CONCAT(index_user.name SEPARATOR ', ')
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
			(index_usersettings.private OR index_usersubmitted.private) AS private,
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
GROUP BY
	index_jack.usersubmitted_ptr_id
ORDER BY %s LIMIT %s"""

		ownerQuery = """,CASE WHEN index_user.id = "%s" THEN 1 ELSE 0 END AS isowner""" % perspective
		voteDirectionQuery = """,( SELECT index_vote.points FROM index_vote INNER JOIN index_usersubmitted ON index_vote.usersubmitted_ptr_id = index_usersubmitted.id INNER JOIN index_user ON index_usersubmitted.user_id = index_user.id WHERE index_vote.jack_id = index_jack.usersubmitted_ptr_id AND index_user.id = "%s") AS vote_direction""" % perspective
		scoreQuery = """,( 100 + ((CHAR_LENGTH(index_jack.comment) / 160) * 200) - (POW(TIMESTAMPDIFF(SECOND,index_jack.date,UTC_TIMESTAMP()) / (60 * 60), 3) * 2) + (CASE WHEN IFNULL(SUM(index_vote.points), 0) > 0 THEN POW(IFNULL(SUM(index_vote.points), 0), 2) * 100 ELSE IFNULL(SUM(index_vote.points), 0) * 100 END) ) AS score"""

		orderDateQuery = """index_jack.date DESC"""
		orderScoreQuery = """score DESC"""

		query = baseQuery % (
				ownerQuery if perspective is not None else "",
				voteDirectionQuery if perspective is not None else "",
				scoreQuery if score else "",
				perspective if perspective is not None else "",
				orderScoreQuery if score else orderDateQuery,
				limit
			)

		#return self.order_by('date').reverse() \
			#.select_related('image', 'link', 'location', 'user', 'ip') \
			#.prefetch_related('bros', 'vote', 'vote__user') \
			#.annotate(votes=Sum('vote__points'))

		return self.raw(query)

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
