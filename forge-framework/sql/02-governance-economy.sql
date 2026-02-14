CREATE TABLE IF NOT EXISTS proposals (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  body TEXT NOT NULL,
  proposer VARCHAR(128) REFERENCES members(address) NOT NULL,
  status VARCHAR(32) DEFAULT 'active',
  votes_for INTEGER DEFAULT 0,
  votes_against INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  execution_tx VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS trades (
  id SERIAL PRIMARY KEY,
  buyer_agent VARCHAR(128) REFERENCES agents(agentid) NOT NULL,
  seller_agent VARCHAR(128) REFERENCES agents(agentid) NOT NULL,
  resource_type VARCHAR(32) NOT NULL,
  amount DOUBLE PRECISION NOT NULL,
  price DOUBLE PRECISION NOT NULL,
  status VARCHAR(32) DEFAULT 'requested',
  escrow_tx VARCHAR(128),
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_budgets (
  agent_id VARCHAR(128) PRIMARY KEY REFERENCES agents(agentid),
  daily_limit DOUBLE PRECISION DEFAULT 100,
  weekly_limit DOUBLE PRECISION DEFAULT 500,
  spent_today DOUBLE PRECISION DEFAULT 0,
  spent_this_week DOUBLE PRECISION DEFAULT 0,
  last_reset_daily TIMESTAMP DEFAULT NOW(),
  last_reset_weekly TIMESTAMP DEFAULT NOW()
);
