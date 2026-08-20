-- DB schema for fb farm

CREATE TABLE accounts (
  id SERIAL PRIMARY KEY,
  login TEXT NOT NULL,
  email TEXT,
  twofa_secret TEXT,
  status TEXT DEFAULT 'unknown',
  profile_id TEXT,
  last_seen TIMESTAMP
);

CREATE TABLE proxies (
  id SERIAL PRIMARY KEY,
  host TEXT NOT NULL,
  port INT NOT NULL,
  scheme TEXT NOT NULL,
  country TEXT,
  last_checked TIMESTAMP,
  rotation_url TEXT
);

CREATE TABLE sessions (
  id SERIAL PRIMARY KEY,
  account_id INT REFERENCES accounts(id),
  cookies JSONB,
  local_storage JSONB,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE logs (
  id SERIAL PRIMARY KEY,
  account_id INT,
  log_type TEXT,
  path TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE twofa_sessions (
  id SERIAL PRIMARY KEY,
  token TEXT UNIQUE NOT NULL,
  account_id INT REFERENCES accounts(id),
  code TEXT,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT now(),
  expires_at TIMESTAMP,
  used_at TIMESTAMP
);
