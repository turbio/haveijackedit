--the queries inside the model are based on what is in this file
SELECT
	`index_jack`.`usersubmitted_ptr_id`,
	`index_usersubmitted`.`private` AS private,
	`index_jack`.`comment` AS comment,
	IFNULL(SUM(index_vote.points), 0) AS votes,
	`index_user`.`name` AS user_name,
	`index_ip`.`address` AS ip_address,
	`index_geolocation`.`lat` AS location_lat,
	`index_geolocation`.`lng` AS location_lng,
	`index_link`.`url` AS url,
	`index_image`.`data` AS image_file,
	`index_image`.`source` AS image_source,
	CASE
	WHEN TIMESTAMPDIFF(SECOND,`index_jack`.`date`,UTC_TIMESTAMP()) < 60
		THEN CONCAT(TIMESTAMPDIFF(SECOND,`index_jack`.`date`,UTC_TIMESTAMP())," seconds ago")
	WHEN TIMESTAMPDIFF(MINUTE,`index_jack`.`date`,UTC_TIMESTAMP()) < 60
		THEN CONCAT(TIMESTAMPDIFF(MINUTE,`index_jack`.`date`,UTC_TIMESTAMP())," minutes ago")
	WHEN TIMESTAMPDIFF(HOUR,`index_jack`.`date`,UTC_TIMESTAMP()) < 60
		THEN CONCAT(TIMESTAMPDIFF(HOUR,`index_jack`.`date`,UTC_TIMESTAMP())," hours ago")
	ELSE
		CONCAT(TIMESTAMPDIFF(DAY,`index_jack`.`date`,UTC_TIMESTAMP())," days ago")
	END AS age,
	(
		SELECT
			GROUP_CONCAT(`index_user`.`name` SEPARATOR ', ')
		FROM
			`index_jack_bros`
		INNER JOIN `index_user` ON
			`index_jack_bros`.`user_id` = `index_user`.`id`
		WHERE
			`index_jack_bros`.`jack_id` = `index_jack`.`usersubmitted_ptr_id`
	) AS bro,
	(
		100
		+ ((CHAR_LENGTH(`index_jack`.`comment`) / 160) * 200)
		- (POW(TIMESTAMPDIFF(SECOND,`index_jack`.`date`,UTC_TIMESTAMP()) / (60 * 60), 3) * 2)
		+ (CASE
		WHEN IFNULL(SUM(index_vote.points), 0) > 0
			THEN POW(IFNULL(SUM(index_vote.points), 0), 2) * 100
		ELSE
			IFNULL(SUM(index_vote.points), 0) * 100
		END)

	)
	AS score,
	(
		SELECT
			`index_vote`.`points`
		FROM
			`index_vote`
		INNER JOIN `index_usersubmitted` ON
			`index_vote`.`usersubmitted_ptr_id` = `index_usersubmitted`.`id`
		INNER JOIN `index_user` ON
			`index_usersubmitted`.`user_id` = `index_user`.`id`
		WHERE
			`index_vote`.`jack_id` = `index_jack`.`usersubmitted_ptr_id`
			AND `index_user`.`name` = "test"
	) AS vote_direction,
	CASE
		WHEN `index_user`.`name` = "test"
			THEN 1
		ELSE 0
	END AS isowner
FROM
	`index_jack`
LEFT OUTER JOIN `index_vote` ON
	( `index_jack`.`usersubmitted_ptr_id` = `index_vote`.`jack_id` )
INNER JOIN `index_usersubmitted` ON
	( `index_jack`.`usersubmitted_ptr_id` = `index_usersubmitted`.`id` )
LEFT OUTER JOIN `index_user` ON
	( `index_usersubmitted`.`user_id` = `index_user`.`id` )
INNER JOIN `index_ip` ON
	( `index_usersubmitted`.`ip_id` = `index_ip`.`id` )
LEFT OUTER JOIN `index_geolocation` ON
	( `index_jack`.`location_id` = `index_geolocation`.`usersubmitted_ptr_id` )
LEFT OUTER JOIN `index_link` ON
	( `index_jack`.`link_id` = `index_link`.`usersubmitted_ptr_id` )
LEFT OUTER JOIN `index_image` ON
	( `index_jack`.`image_id` = `index_image`.`usersubmitted_ptr_id` )
GROUP BY
	`index_jack`.`usersubmitted_ptr_id`
ORDER BY
	-- `index_jack`.`date` DESC
	score DESC
LIMIT 25
