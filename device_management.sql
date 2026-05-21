-- Creating devices and events tables
CREATE TABLE devices (
  device_id   INTEGER PRIMARY KEY,
  label       TEXT NOT NULL,
  owner_email TEXT NOT NULL,
  city        TEXT NOT NULL
);

CREATE TABLE events (
  event_id    INTEGER PRIMARY KEY,
  device_id   INTEGER NOT NULL REFERENCES devices(device_id),
  event_type  TEXT NOT NULL,
  payload     TEXT NOT NULL,
  created_at  TIMESTAMP NOT NULL
);

-- Inserting sample data into devices table
INSERT INTO devices VALUES
  (1, 'Edge-Node-A', 'a@example.com', 'Bengaluru'),
  (2, 'Edge-Node-B', 'b@example.com', 'Bengaluru'),
  (3, 'Gateway-01',  'c@example.com', 'Pune'),
  (4, 'Gateway-02',  'd@example.com', 'Mumbai');

INSERT INTO events VALUES
  (101, 1, 'boot',   'ok',  TIMESTAMP '2026-05-01 09:00:00'),
  (102, 1, 'error',  'e1',  TIMESTAMP '2026-05-02 10:05:00'),
  (103, 2, 'boot',   'ok',  TIMESTAMP '2026-05-03 08:10:00'),
  (104, 3, 'sync',   's1',  TIMESTAMP '2026-05-04 11:20:00'),
  (105, 3, 'error',  'e2',  TIMESTAMP '2026-05-05 12:30:00'),
  (106, 4, 'boot',   'ok',  TIMESTAMP '2026-05-06 07:40:00'),
  (107, 1, 'sync',   's2',  TIMESTAMP '2026-05-07 13:50:00'),
  (108, 2, 'error',  'e3',  TIMESTAMP '2026-05-08 14:55:00'),
  (109, 4, 'sync',   's3',  TIMESTAMP '2026-05-09 15:10:00'),
  (110, 3, 'boot',   'ok',  TIMESTAMP '2026-05-10 16:25:00');

-- Newest errors first (cap + sort):
SELECT event_id , device_id , payload , created_at
FROM events
WHERE event_type = 'error' 
ORDER BY created_at DESC
LIMIT 3;

-- Stable pagination (page 2):
SELECT event_id , device_id , event_type , created_at
FROM events
ORDER BY event_id
LIMIT 4
OFFSET 4

-- Text pattern filter on devices:
SELECT device_id , label , owner_email
FROM devices
WHERE label LIKE '%way%'

-- Inner join report + filter + sort:
SELECT devices.label , events.event_type , events.created_at
FROM devices
INNER JOIN events ON devices.device_id = events.device_id
WHERE devices.city = 'Bengaluru' AND events.event_type = 'error'
ORDER BY events.created_at;