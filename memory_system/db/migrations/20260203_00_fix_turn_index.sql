-- fix_turn_index.sql
-- Re-number turn_index per (user_id, session_id) to eliminate duplicates.
-- Order by created_at, id to preserve chronology.

WITH ranked AS (
  SELECT id,
         user_id,
         session_id,
         ROW_NUMBER() OVER (PARTITION BY user_id, session_id ORDER BY created_at, id) AS rn
  FROM chat_turns
)
UPDATE chat_turns t
SET turn_index = r.rn
FROM ranked r
WHERE t.id = r.id;
