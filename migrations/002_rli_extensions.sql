-- RLI Integration Schema Extensions
-- Adds tables and columns for Remote Labor Index evaluation tracking

-- ========== RLI EVALUATIONS TABLE ==========

CREATE TABLE IF NOT EXISTS rli_evaluations (
    evaluation_id VARCHAR(64) PRIMARY KEY,
    agent_id VARCHAR(64),
    owner_address VARCHAR(42) NOT NULL,
    task_id INTEGER NOT NULL,
    task_category VARCHAR(32),
    task_brief TEXT,
    automation_rate DECIMAL(4,2) CHECK (automation_rate >= 0 AND automation_rate <= 1),
    elo_score INTEGER,
    economic_value DECIMAL(10,2),
    rep_earned INTEGER,
    evaluation_timestamp TIMESTAMP DEFAULT NOW(),
    rli_comparison_url TEXT,
    chainlink_request_id VARCHAR(66),
    status VARCHAR(20) DEFAULT 'pending',
    CONSTRAINT fk_agent FOREIGN KEY (agent_id) REFERENCES agents(agentid) ON DELETE SET NULL
);

CREATE INDEX idx_rli_agent ON rli_evaluations(agent_id);
CREATE INDEX idx_rli_owner ON rli_evaluations(owner_address);
CREATE INDEX idx_rli_timestamp ON rli_evaluations(evaluation_timestamp DESC);
CREATE INDEX idx_rli_status ON rli_evaluations(status);

COMMENT ON TABLE rli_evaluations IS 'Tracks RLI (Remote Labor Index) evaluation results for agent performance';

-- ========== EXTEND AGENTS TABLE ==========

ALTER TABLE agents 
  ADD COLUMN IF NOT EXISTS rli_avg_automation DECIMAL(4,2) DEFAULT 0.00,
  ADD COLUMN IF NOT EXISTS rli_tasks_completed INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS rli_tier_qualified BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS rli_last_eval_at TIMESTAMP;

COMMENT ON COLUMN agents.rli_avg_automation IS 'Rolling average of automation rate across all RLI evaluations';
COMMENT ON COLUMN agents.rli_tasks_completed IS 'Total number of RLI tasks completed by this agent';
COMMENT ON COLUMN agents.rli_tier_qualified IS 'Whether agent meets RLI requirements for tier upgrades';

-- ========== RLI TASK QUEUE TABLE ==========

CREATE TABLE IF NOT EXISTS rli_task_queue (
    queue_id SERIAL PRIMARY KEY,
    agent_id VARCHAR(64),
    task_category VARCHAR(32) NOT NULL,
    deliverable_ipfs_hash VARCHAR(64) NOT NULL,
    priority INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'queued',
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    CONSTRAINT fk_agent_queue FOREIGN KEY (agent_id) REFERENCES agents(agentid) ON DELETE CASCADE
);

CREATE INDEX idx_queue_status ON rli_task_queue(status, priority DESC);

COMMENT ON TABLE rli_task_queue IS 'Queue for pending RLI evaluation requests';

-- ========== RLI BUDGET TRACKING ==========

CREATE TABLE IF NOT EXISTS rli_budget (
    id SERIAL PRIMARY KEY,
    total_budget INTEGER NOT NULL,
    evaluations_used INTEGER DEFAULT 0,
    evaluations_remaining INTEGER GENERATED ALWAYS AS (total_budget - evaluations_used) STORED,
    last_replenish_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Initialize budget
INSERT INTO rli_budget (total_budget, evaluations_used)
VALUES (100, 0)
ON CONFLICT DO NOTHING;

COMMENT ON TABLE rli_budget IS 'Tracks available RLI evaluation budget';

-- ========== VIEWS ==========

-- View: Top performers by RLI score
CREATE OR REPLACE VIEW rli_top_performers AS
SELECT 
    a.agentid,
    a.agenttype,
    a.owneraddress,
    a.rli_avg_automation,
    a.rli_tasks_completed,
    MAX(e.elo_score) as max_elo_score,
    AVG(e.economic_value) as avg_task_value,
    a.tier
FROM agents a
LEFT JOIN rli_evaluations e ON a.agentid = e.agent_id
WHERE a.rli_tasks_completed > 0
GROUP BY a.agentid, a.agenttype, a.owneraddress, a.rli_avg_automation, a.rli_tasks_completed, a.tier
ORDER BY a.rli_avg_automation DESC, a.rli_tasks_completed DESC
LIMIT 100;

COMMENT ON VIEW rli_top_performers IS 'Top 100 agents ranked by RLI performance metrics';

-- View: RLI qualification status
CREATE OR REPLACE VIEW rli_qualification_status AS
SELECT 
    owneraddress,
    COUNT(*) as total_agents,
    SUM(CASE WHEN rli_tier_qualified THEN 1 ELSE 0 END) as qualified_agents,
    AVG(rli_avg_automation) as avg_automation_rate,
    SUM(rli_tasks_completed) as total_tasks_completed
FROM agents
WHERE tier >= 1
GROUP BY owneraddress
ORDER BY avg_automation_rate DESC;

COMMENT ON VIEW rli_qualification_status IS 'Summary of RLI qualification status by owner';

-- ========== FUNCTIONS ==========

-- Function: Update agent RLI stats after evaluation
CREATE OR REPLACE FUNCTION update_agent_rli_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND NEW.agent_id IS NOT NULL THEN
        UPDATE agents
        SET 
            rli_tasks_completed = rli_tasks_completed + 1,
            rli_avg_automation = (
                (rli_avg_automation * rli_tasks_completed + NEW.automation_rate) / 
                (rli_tasks_completed + 1)
            ),
            rli_last_eval_at = NEW.evaluation_timestamp,
            rli_tier_qualified = (
                -- Check Tier 2 requirements
                (rli_tasks_completed + 1 >= 3 AND 
                 (rli_avg_automation * rli_tasks_completed + NEW.automation_rate) / (rli_tasks_completed + 1) >= 0.50)
                OR
                -- Check Tier 3 requirements
                (rli_tasks_completed + 1 >= 5 AND 
                 (rli_avg_automation * rli_tasks_completed + NEW.automation_rate) / (rli_tasks_completed + 1) >= 0.70)
            )
        WHERE agentid = NEW.agent_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_rli_stats
AFTER INSERT OR UPDATE ON rli_evaluations
FOR EACH ROW
EXECUTE FUNCTION update_agent_rli_stats();

COMMENT ON FUNCTION update_agent_rli_stats IS 'Automatically updates agent RLI statistics when new evaluation is recorded';

-- Function: Check RLI budget and auto-replenish
CREATE OR REPLACE FUNCTION check_rli_budget()
RETURNS TRIGGER AS $$
DECLARE
    remaining INTEGER;
BEGIN
    SELECT evaluations_remaining INTO remaining FROM rli_budget LIMIT 1;
    
    IF remaining < 20 THEN
        -- Auto-replenish logic (would trigger external notification)
        -- For now, just log
        RAISE NOTICE 'RLI budget low: % evaluations remaining', remaining;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_budget
AFTER UPDATE ON rli_budget
FOR EACH ROW
EXECUTE FUNCTION check_rli_budget();

-- ========== SEED DATA ==========

-- Add sample task categories
CREATE TABLE IF NOT EXISTS rli_task_categories (
    category VARCHAR(32) PRIMARY KEY,
    description TEXT,
    avg_completion_time_minutes INTEGER,
    avg_cost_usd DECIMAL(6,2)
);

INSERT INTO rli_task_categories (category, description, avg_completion_time_minutes, avg_cost_usd) VALUES
('web-development', 'Web development tasks (React, Vue, backend APIs)', 180, 50.00),
('data-visualization', 'Data visualization and dashboard creation', 120, 35.00),
('3d-rendering', 'CAD, product design, architecture rendering', 240, 75.00),
('document-preparation', 'Scientific documents, presentations, reports', 90, 25.00),
('video-editing', 'Video editing and animation tasks', 150, 45.00),
('audio-production', 'Audio editing, music production', 120, 40.00)
ON CONFLICT (category) DO NOTHING;

-- ========== GRANTS ==========

-- Grant permissions (adjust role name as needed)
-- GRANT SELECT, INSERT, UPDATE ON rli_evaluations TO forge_backend;
-- GRANT SELECT, INSERT, UPDATE ON rli_task_queue TO forge_backend;
-- GRANT SELECT, UPDATE ON rli_budget TO forge_backend;
-- GRANT SELECT ON rli_top_performers TO forge_backend;
-- GRANT SELECT ON rli_qualification_status TO forge_backend;

COMMIT;
