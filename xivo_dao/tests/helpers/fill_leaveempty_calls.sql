DROP FUNCTION IF EXISTS "fill_leaveempty_calls" (timestamptz, timestamptz);
CREATE OR REPLACE FUNCTION "fill_leaveempty_calls" (period_start timestamptz, period_end timestamptz)
RETURNS void AS
$$
INSERT INTO stat_call_on_queue (callid, time, waittime, stat_queue_id, status)
SELECT
callid,
enter_time as time,
EXTRACT(EPOCH FROM (leave_time - enter_time))::INTEGER as waittime,
stat_queue_id,
'leaveempty' AS status
FROM (SELECT
    time AS enter_time,
    (select time from queue_log where callid=main.callid AND event='LEAVEEMPTY' LIMIT 1) AS leave_time,
    callid,
    (SELECT id FROM stat_queue WHERE name=queuename) AS stat_queue_id
  FROM queue_log AS main
  WHERE callid IN (SELECT callid FROM queue_log WHERE event = 'LEAVEEMPTY')
        AND event = 'ENTERQUEUE'
        AND time BETWEEN $1 AND $2) AS first;
$$
LANGUAGE SQL;

