-- Performance optimization indexes and business logic functions
-- This migration adds essential indexes and business logic functions

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
