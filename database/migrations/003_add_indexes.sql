-- Performance optimization indexes and business logic functions
-- This migration adds essential indexes and business logic functions

-- Add missing JIRA tables (added after initial schema)
CREATE TABLE IF NOT EXISTS board (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS status_column (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    board_id INTEGER NOT NULL REFERENCES board(id) ON DELETE CASCADE,
    "order" INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ticket (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assignee VARCHAR(255),
    conversation TEXT,
    column_id INTEGER NOT NULL REFERENCES status_column(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ticketcomment (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES ticket(id) ON DELETE CASCADE,
    author VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS webhook (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) NOT NULL,
    event_code VARCHAR(100) NOT NULL
);

-- Indexes for JIRA tables
CREATE INDEX IF NOT EXISTS idx_board_name ON board(name);
CREATE INDEX IF NOT EXISTS idx_status_column_board_id ON status_column(board_id);
CREATE INDEX IF NOT EXISTS idx_status_column_order ON status_column("order");
CREATE INDEX IF NOT EXISTS idx_ticket_column_id ON ticket(column_id);
CREATE INDEX IF NOT EXISTS idx_ticket_assignee ON ticket(assignee);
CREATE INDEX IF NOT EXISTS idx_ticket_title_fts ON ticket USING GIN(to_tsvector('english', title || ' ' || COALESCE(description, '')));
CREATE INDEX IF NOT EXISTS idx_ticketcomment_ticket_id ON ticketcomment(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticketcomment_timestamp ON ticketcomment(timestamp);
CREATE INDEX IF NOT EXISTS idx_ticketcomment_author ON ticketcomment(author);
CREATE INDEX IF NOT EXISTS idx_webhook_event_code ON webhook(event_code);
CREATE INDEX IF NOT EXISTS idx_webhook_url ON webhook(url);

-- Specialized indexes for time-based queries
CREATE INDEX IF NOT EXISTS idx_tasks_deadline_status ON tasks(deadline, status) WHERE deadline IS NOT NULL AND status NOT IN ('completed', 'failed');
CREATE INDEX IF NOT EXISTS idx_task_assignments_completion_time ON task_assignments(completed_at, status) WHERE completed_at IS NOT NULL;

-- Basic indexes for performance monitoring
CREATE INDEX IF NOT EXISTS idx_agents_performance_metrics ON agents USING GIN(performance_metrics) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_task_assignments_quality_score ON task_assignments(quality_score) WHERE quality_score IS NOT NULL;

-- Indexes for skill matching queries
CREATE INDEX IF NOT EXISTS idx_job_descriptions_skills_experience ON job_descriptions USING GIN(required_skills) WHERE experience_level IS NOT NULL;

-- Indexes for audit trail efficiency
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Full-text search indexes for text fields
CREATE INDEX IF NOT EXISTS idx_job_descriptions_fts ON job_descriptions USING GIN(to_tsvector('english', title || ' ' || description));
CREATE INDEX IF NOT EXISTS idx_tasks_fts ON tasks USING GIN(to_tsvector('english', title || ' ' || description));
CREATE INDEX IF NOT EXISTS idx_resumes_fts ON resumes USING GIN(to_tsvector('english', name || ' ' || COALESCE(summary, '')));

-- Partial indexes for frequently filtered data
CREATE INDEX IF NOT EXISTS idx_tasks_pending_by_priority ON tasks(priority, created_at) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_tasks_blocked_by_priority ON tasks(priority, created_at) WHERE status = 'blocked';
CREATE INDEX IF NOT EXISTS idx_job_applications_pending ON job_applications(application_date) WHERE status IN ('applied', 'interviewing');

-- Composite indexes for complex joins
CREATE INDEX IF NOT EXISTS idx_task_assignments_agent_task_status ON task_assignments(agent_id, task_id, status, assigned_at);
CREATE INDEX IF NOT EXISTS idx_execution_costs_comprehensive ON execution_costs(agent_id, model_name, execution_type, created_at);

-- Additional indexes for JSON/JSONB performance optimization
CREATE INDEX IF NOT EXISTS idx_agents_configuration ON agents USING GIN(configuration);
CREATE INDEX IF NOT EXISTS idx_agents_execution_parameters ON agents USING GIN(execution_parameters);
CREATE INDEX IF NOT EXISTS idx_tasks_metadata ON tasks USING GIN(task_metadata);
CREATE INDEX IF NOT EXISTS idx_tasks_dependencies ON tasks USING GIN(dependencies);
CREATE INDEX IF NOT EXISTS idx_tasks_blockers ON tasks USING GIN(blockers);
CREATE INDEX IF NOT EXISTS idx_execution_costs_metadata ON execution_costs USING GIN(execution_metadata);
CREATE INDEX IF NOT EXISTS idx_resumes_experience ON resumes USING GIN(experience);
CREATE INDEX IF NOT EXISTS idx_resumes_education ON resumes USING GIN(education);
CREATE INDEX IF NOT EXISTS idx_resumes_performance_history ON resumes USING GIN(performance_history);
CREATE INDEX IF NOT EXISTS idx_audit_logs_old_values ON audit_logs USING GIN(old_values);
CREATE INDEX IF NOT EXISTS idx_audit_logs_new_values ON audit_logs USING GIN(new_values);
CREATE INDEX IF NOT EXISTS idx_audit_logs_metadata ON audit_logs USING GIN(metadata);

-- Indexes for cost aggregation and reporting
CREATE INDEX IF NOT EXISTS idx_execution_costs_cost_analysis ON execution_costs(created_at, total_cost, agent_id, model_name);
CREATE INDEX IF NOT EXISTS idx_task_assignments_cost_tracking ON task_assignments(assigned_at, actual_cost, agent_id) WHERE actual_cost IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tasks_cost_estimation ON tasks(estimated_cost, actual_cost, status) WHERE estimated_cost IS NOT NULL;

-- Indexes for agent performance monitoring
CREATE INDEX IF NOT EXISTS idx_agents_model_status ON agents(model_name, status, created_at);
CREATE INDEX IF NOT EXISTS idx_task_assignments_performance ON task_assignments(agent_id, quality_score, completed_at) WHERE quality_score IS NOT NULL;

-- Indexes for prompt management queries
CREATE INDEX IF NOT EXISTS idx_task_prompts_type_active ON task_prompts(task_type, is_active, version);
CREATE INDEX IF NOT EXISTS idx_resume_prompts_persona_active ON resume_prompts(persona_type, is_active, version);

-- Indexes for resume and job matching
CREATE INDEX IF NOT EXISTS idx_resumes_skills_performance ON resumes USING GIN(skills) WHERE performance_history IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_job_descriptions_title_department ON job_descriptions(department, experience_level, created_at);

-- Indexes for application lifecycle tracking
CREATE INDEX IF NOT EXISTS idx_job_applications_status_date ON job_applications(status, application_date, job_description_id);

-- Indexes for model catalog optimization
CREATE INDEX IF NOT EXISTS idx_model_catalog_cost_performance ON model_catalog(cost_per_input_token, cost_per_output_token, performance_tier) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_model_catalog_capabilities ON model_catalog USING GIN(capabilities) WHERE is_active = true;

-- Add additional constraints
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'check_completion_after_assignment'
    ) THEN
        ALTER TABLE task_assignments ADD CONSTRAINT check_completion_after_assignment 
            CHECK (completed_at IS NULL OR completed_at >= assigned_at);
    END IF;
END $$;

-- Function to automatically update task status based on assignments
CREATE OR REPLACE FUNCTION update_task_status_on_assignment_change()
RETURNS TRIGGER AS $$
BEGIN
    -- When an assignment is completed, check if all assignments for the task are done
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        -- Check if this was the last pending assignment
        IF NOT EXISTS (
            SELECT 1 FROM task_assignments 
            WHERE task_id = NEW.task_id 
            AND status NOT IN ('completed', 'failed', 'reassigned')
            AND id != NEW.id
        ) THEN
            UPDATE tasks SET 
                status = 'completed',
                completed_at = CURRENT_TIMESTAMP,
                actual_cost = (
                    SELECT SUM(actual_cost) 
                    FROM task_assignments 
                    WHERE task_id = NEW.task_id 
                    AND actual_cost IS NOT NULL
                )
            WHERE id = NEW.task_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update task status
CREATE TRIGGER task_assignment_status_trigger 
    AFTER UPDATE ON task_assignments
    FOR EACH ROW 
    EXECUTE FUNCTION update_task_status_on_assignment_change();

-- Function to enforce business rules on agent status changes
CREATE OR REPLACE FUNCTION validate_agent_status_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Prevent terminating agents with active assignments
    IF NEW.status = 'terminated' AND OLD.status != 'terminated' THEN
        IF EXISTS (
            SELECT 1 FROM task_assignments ta
            JOIN tasks t ON ta.task_id = t.id
            WHERE ta.agent_id = NEW.id 
            AND ta.status IN ('assigned', 'accepted', 'in_progress')
            AND t.status NOT IN ('completed', 'failed')
        ) THEN
            RAISE EXCEPTION 'Cannot terminate agent with active task assignments';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for agent status validation
CREATE TRIGGER agent_status_validation_trigger 
    BEFORE UPDATE ON agents
    FOR EACH ROW 
    EXECUTE FUNCTION validate_agent_status_change();

-- Add a utility function to calculate agent utilization
CREATE OR REPLACE FUNCTION calculate_agent_utilization(agent_id_param INTEGER, days_back INTEGER DEFAULT 30)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    total_assignments INTEGER;
    completed_assignments INTEGER;
    utilization DECIMAL(5,2);
BEGIN
    SELECT COUNT(*) INTO total_assignments
    FROM task_assignments ta
    WHERE ta.agent_id = agent_id_param
    AND ta.assigned_at >= CURRENT_DATE - INTERVAL '1 day' * days_back;
    
    SELECT COUNT(*) INTO completed_assignments
    FROM task_assignments ta
    WHERE ta.agent_id = agent_id_param
    AND ta.status = 'completed'
    AND ta.assigned_at >= CURRENT_DATE - INTERVAL '1 day' * days_back;
    
    IF total_assignments = 0 THEN
        RETURN 0.0;
    END IF;
    
    utilization := (completed_assignments::DECIMAL / total_assignments::DECIMAL) * 100.0;
    RETURN ROUND(utilization, 2);
END;
$$ LANGUAGE plpgsql;

-- Add comments for the new functions
COMMENT ON FUNCTION update_task_status_on_assignment_change() IS 'Automatically updates task status when all assignments are completed';
COMMENT ON FUNCTION validate_agent_status_change() IS 'Validates business rules when changing agent status';
COMMENT ON FUNCTION calculate_agent_utilization(INTEGER, INTEGER) IS 'Calculates agent utilization percentage over specified time period';

-- Add comments for the new JIRA tables
COMMENT ON TABLE board IS 'JIRA boards for organizing tickets';
COMMENT ON TABLE status_column IS 'Status columns within JIRA boards for ticket workflow';
COMMENT ON TABLE ticket IS 'JIRA tickets representing work items';
COMMENT ON TABLE ticketcomment IS 'Comments on JIRA tickets for collaboration';
COMMENT ON TABLE webhook IS 'Webhook endpoints for JIRA event notifications';
