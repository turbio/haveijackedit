SELECT
	index_jack.usersubmitted_ptr_id,
	index_jack.comment          AS comment,
	IFNULL(SUM(index_vote.points), 0)      AS votes,
	index_user.name             AS user_name,
	index_ip.address            AS ip_address,
	index_usersubmitted.private AS private,
	index_geolocation.lat       AS location_lat,
	index_geolocation.lng       AS location_lng,
	index_image.data            AS image_file,
	index_image.source          AS image_source,
	index_link.url              AS url,
	julianday(index_jack.date) AS age
	-- (julianday('now') - julianday(index_jack.date)) AS age
FROM
	index_jack
LEFT OUTER JOIN index_vote
	ON index_jack.usersubmitted_ptr_id = index_vote.jack_id
INNER JOIN index_usersubmitted
	ON index_jack.usersubmitted_ptr_id = index_usersubmitted.id
LEFT OUTER JOIN index_user
	ON index_usersubmitted.user_id = index_user.id
INNER JOIN index_ip
	ON index_usersubmitted.ip_id = index_ip.id
LEFT OUTER JOIN index_geolocation
	ON index_jack.location_id = index_geolocation.usersubmitted_ptr_id
LEFT OUTER JOIN index_usersubmitted T7
	ON index_geolocation.usersubmitted_ptr_id = T7.id
LEFT OUTER JOIN index_link
	ON index_jack.link_id = index_link.usersubmitted_ptr_id
LEFT OUTER JOIN index_usersubmitted T9
	ON index_link.usersubmitted_ptr_id = T9.id
LEFT OUTER JOIN index_image
	ON index_jack.image_id = index_image.usersubmitted_ptr_id
LEFT OUTER JOIN index_usersubmitted T11
	ON index_image.usersubmitted_ptr_id = T11.id
GROUP  BY index_usersubmitted.id,
	index_usersubmitted.user_id,
	index_usersubmitted.ip_id,
	index_usersubmitted.private,
	index_usersubmitted.hidden,
	index_jack.usersubmitted_ptr_id,
	index_jack.date,
	index_jack.comment,
	index_jack.location_id,
	index_jack.link_id,
	index_jack.image_id,
	index_user.id,
	index_user.name,
	index_user.password_hash,
	index_user.password_salt,
	index_user.last_online,
	index_user.creation_date,
	index_user.settings_id,
	index_ip.id,
	index_ip.address,
	index_geolocation.usersubmitted_ptr_id,
	index_geolocation.lat,
	index_geolocation.lng,
	T9.id,
	T9.user_id,
	T9.ip_id,
	T9.private,
	T9.hidden,
	index_link.usersubmitted_ptr_id,
	index_link.url,
	T11.id,
	T11.user_id,
	T11.ip_id,
	T11.private,
	T11.hidden,
	index_image.usersubmitted_ptr_id,
	index_image.data,
	index_image.source
ORDER  BY
	index_jack.date DESC
