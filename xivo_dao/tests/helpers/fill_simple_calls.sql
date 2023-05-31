DROP FUNCTION IF EXISTS "fill_simple_calls" (timestamptz, timestamptz);
CREATE FUNCTION "fill_simple_calls"(period_start timestamptz, period_end timestamptz)
  RETURNS void AS
$$
  INSERT INTO "stat_call_on_queue" (callid, "time", stat_queue_id, status)
    SELECT
      callid,
      time,
      (SELECT id FROM stat_queue WHERE name=queuename) as stat_queue_id,
      CASE WHEN event = 'FULL' THEN 'full'::call_exit_type
           WHEN event = 'DIVERT_CA_RATIO' THEN 'divert_ca_ratio'
           WHEN event = 'DIVERT_HOLDTIME' THEN 'divert_waittime'
           WHEN event = 'CLOSED' THEN 'closed'
           WHEN event = 'JOINEMPTY' THEN 'joinempty'
      END as status
    FROM queue_log
    WHERE event IN ('FULL', 'DIVERT_CA_RATIO', 'DIVERT_HOLDTIME', 'CLOSED', 'JOINEMPTY') AND
          "time" BETWEEN $1 AND $2;
$$
LANGUAGE SQL;

