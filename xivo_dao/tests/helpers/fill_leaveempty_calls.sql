DROP FUNCTION IF EXISTS "fill_leaveempty_calls" (timestamptz, timestamptz);
CREATE OR REPLACE FUNCTION "fill_leaveempty_calls" (period_start timestamptz, period_end timestamptz)
RETURNS void AS
$$
WITH 
leave_call as (
    select main.id, main.callid, main.time as leave_time, main.queuename, 
        (select time from queue_log 
        where callid = main.callid and queuename = main.queuename 
        and time <= main.time and event = 'ENTERQUEUE' 
        order by time desc limit 1) as enter_time, 
        stat_queue.id as stat_queue_id 
    from queue_log as main 
    left join stat_queue on stat_queue.name = main.queuename
    where event='LEAVEEMPTY'
),
leave_call_in_range as (
    select *
    from leave_call
    where enter_time BETWEEN $1 AND $2 
)
INSERT INTO stat_call_on_queue (callid, time, waittime, stat_queue_id, status)
SELECT
callid,
enter_time as time,
EXTRACT(EPOCH FROM (leave_time - enter_time))::INTEGER as waittime,
stat_queue_id,
'leaveempty' AS status
FROM leave_call_in_range;
$$
LANGUAGE SQL;
 
