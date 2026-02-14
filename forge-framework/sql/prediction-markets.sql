CREATE TABLE IF NOT EXISTS prediction_markets (
  id SERIAL PRIMARY KEY,
  question TEXT NOT NULL,
  market_type INTEGER NOT NULL,
  resolution_date TIMESTAMP NOT NULL,
  final_price NUMERIC,
  resolved BOOLEAN DEFAULT FALSE,
  creator VARCHAR(128) NOT NULL
);

CREATE TABLE IF NOT EXISTS prediction_positions (
  id SERIAL PRIMARY KEY,
  market_id INTEGER REFERENCES prediction_markets(id),
  trader VARCHAR(128) NOT NULL,
  yes_stake NUMERIC DEFAULT 0,
  no_stake NUMERIC DEFAULT 0
);
