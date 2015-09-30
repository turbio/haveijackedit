SELECT
	index_user.id,
	(IFNULL(votes.total_recieved, 0) * 5) + jacks.unique_dates + FLOOR(jacks.total_submitted_length / jacks.total_submitted) AS score
FROM
	index_user
LEFT JOIN (
	SELECT
		index_usersubmitted.user_id AS user_id,
		IFNULL(SUM(index_vote.points), 0) AS total_recieved
	FROM
		index_vote
	INNER JOIN index_jack ON
		index_jack.usersubmitted_ptr_id = index_vote.jack_id
	INNER JOIN index_usersubmitted ON
		index_usersubmitted.id = index_jack.usersubmitted_ptr_id
	GROUP BY
		index_usersubmitted.user_id
) AS votes ON votes.user_id = index_user.id
LEFT JOIN (
	SELECT
		index_usersubmitted.user_id AS user_id,
		COUNT(index_jack.usersubmitted_ptr_id) AS total_submitted,
		SUM(CHAR_LENGTH(index_jack.comment)) AS total_submitted_length,
		COUNT(DISTINCT DATE(index_jack.date)) AS unique_dates
	FROM
		index_jack
	INNER JOIN index_usersubmitted ON
		index_usersubmitted.id = index_jack.usersubmitted_ptr_id
	GROUP BY
		index_usersubmitted.user_id
) AS jacks ON jacks.user_id = index_user.id
WHERE index_user.id = %s
