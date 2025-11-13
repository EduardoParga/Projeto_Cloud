CREATE TABLE IF NOT EXISTS quotes (
  id SERIAL PRIMARY KEY,
  ticker TEXT NOT NULL,
  trade_date DATE NOT NULL,
  open NUMERIC,
  close NUMERIC,
  low NUMERIC,
  high NUMERIC,
  volume NUMERIC
);