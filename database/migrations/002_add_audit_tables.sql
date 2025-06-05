-- Additional audit and constraint enhancements
-- This migration adds additional constraints and audit functionality

-- Add additional constraints for data integrity
ALTER TABLE tasks ADD CONSTRAINT check_estimated_cost_positive CHECK (estimated_cost >= 0);
ALTER TABLE tasks ADD CONSTRAINT check_actual_cost_positive CHECK (actual_cost >= 0);
ALTER TABLE task_assignments ADD CONSTRAINT check_cost_estimate_positive CHECK (cost_estimate >= 0);
ALTER TABLE task_assignments ADD CONSTRAINT check_actual_cost_positive CHECK (actual_cost >= 0);
ALTER TABLE execution_costs ADD CONSTRAINT check_input_tokens_positive CHECK (input_tokens >= 0);
ALTER TABLE execution_costs ADD CONSTRAINT check_output_tokens_positive CHECK (output_tokens >= 0);
ALTER TABLE execution_costs ADD CONSTRAINT check_total_cost_positive CHECK (total_cost >= 0);
ALTER TABLE execution_costs ADD CONSTRAINT check_execution_time_positive CHECK (execution_time_ms >= 0);
ALTER TABLE execution_costs ADD CONSTRAINT check_consensus_round_positive CHECK (consensus_round >= 1);

-- Add constraint to ensure only one active agent per job description at a time (business rule)
CREATE UNIQUE INDEX idx_agents_unique_active_job_description 
ON agents(job_description_id) 
WHERE status = 'active';

-- Add constraint to ensure task dependencies make sense (no circular dependencies)
-- This is enforced at application level, but we add a check for basic validation
ALTER TABLE tasks ADD CONSTRAINT check_no_self_parent CHECK (id != parent_task_id);

-- Add partial index for active tasks to improve query performance
CREATE INDEX idx_tasks_active_status ON tasks(status, created_at) WHERE status IN ('pending', 'assigned', 'in_progress', 'blocked');

-- Add partial index for active agents
CREATE INDEX idx_agents_active ON agents(status, model_name) WHERE status = 'active';

-- Add composite indexes for common query patterns
CREATE INDEX idx_task_assignments_task_status ON task_assignments(task_id, status);
CREATE INDEX idx_execution_costs_agent_task ON execution_costs(agent_id, task_id, created_at);
CREATE INDEX idx_audit_logs_entity_action ON audit_logs(entity_type, action, created_at);

-- Add constraint to ensure model costs are reasonable
ALTER TABLE model_catalog ADD CONSTRAINT check_cost_per_input_token_reasonable CHECK (cost_per_input_token >= 0 AND cost_per_input_token <= 1.0);
ALTER TABLE model_catalog ADD CONSTRAINT check_cost_per_output_token_reasonable CHECK (cost_per_output_token >= 0 AND cost_per_output_token <= 1.0);
ALTER TABLE model_catalog ADD CONSTRAINT check_context_limit_positive CHECK (context_limit > 0);

-- Add check constraints for JSONB fields that should have specific structures
-- These are basic checks; more validation should be done at application level
ALTER TABLE job_descriptions ADD CONSTRAINT check_required_skills_is_array CHECK (jsonb_typeof(required_skills) = 'array');
ALTER TABLE resumes ADD CONSTRAINT check_skills_is_array CHECK (jsonb_typeof(skills) = 'array');
ALTER TABLE resumes ADD CONSTRAINT check_experience_is_array CHECK (jsonb_typeof(experience) = 'array');
ALTER TABLE resumes ADD CONSTRAINT check_education_is_array CHECK (jsonb_typeof(education) = 'array');
ALTER TABLE tasks ADD CONSTRAINT check_required_skills_is_array CHECK (jsonb_typeof(required_skills) = 'array');
ALTER TABLE tasks ADD CONSTRAINT check_dependencies_is_array CHECK (jsonb_typeof(dependencies) = 'array');
ALTER TABLE tasks ADD CONSTRAINT check_blockers_is_array CHECK (jsonb_typeof(blockers) = 'array');
ALTER TABLE model_catalog ADD CONSTRAINT check_capabilities_is_array CHECK (jsonb_typeof(capabilities) = 'array');
ALTER TABLE task_prompts ADD CONSTRAINT check_variables_is_array CHECK (jsonb_typeof(variables) = 'array');
ALTER TABLE resume_prompts ADD CONSTRAINT check_variables_is_array CHECK (jsonb_typeof(variables) = 'array');

-- Create views for commonly accessed data combinations
CREATE VIEW active_agents_with_jobs AS
SELECT 
    a.id as agent_id,
    a.name as agent_name,
    a.model_name,
    a.status as agent_status,
    a.performance_metrics,
    r.name as resume_name,
    r.skills as resume_skills,
    jd.title as job_title,
    jd.required_skills as job_required_skills,
    jd.experience_level,
    a.created_at as agent_created_at
FROM agents a
JOIN resumes r ON a.resume_id = r.id
JOIN job_descriptions jd ON a.job_description_id = jd.id
WHERE a.status = 'active';

CREATE VIEW task_status_summary AS
SELECT 
    t.id as task_id,
    t.title,
    t.status,
    t.priority,
    t.estimated_cost,
    t.actual_cost,
    COUNT(ta.id) as assignment_count,
    COUNT(CASE WHEN ta.status = 'completed' THEN 1 END) as completed_assignments,
    COUNT(CASE WHEN ta.status = 'failed' THEN 1 END) as failed_assignments,
    SUM(ta.actual_cost) as total_assignment_cost,
    t.created_at,
    t.completed_at
FROM tasks t
LEFT JOIN task_assignments ta ON t.id = ta.task_id
GROUP BY t.id, t.title, t.status, t.priority, t.estimated_cost, t.actual_cost, t.created_at, t.completed_at;

CREATE VIEW cost_summary_by_agent AS
SELECT 
    a.id as agent_id,
    a.name as agent_name,
    a.model_name,
    COUNT(ec.id) as execution_count,
    SUM(ec.total_cost) as total_cost,
    AVG(ec.total_cost) as avg_cost_per_execution,
    SUM(ec.input_tokens) as total_input_tokens,
    SUM(ec.output_tokens) as total_output_tokens,
    MAX(ec.created_at) as last_execution
FROM agents a
LEFT JOIN execution_costs ec ON a.id = ec.agent_id
GROUP BY a.id, a.name, a.model_name;

-- Add comments for documentation
COMMENT ON TABLE job_descriptions IS 'Stores job descriptions with required skills and experience levels for hiring AI agents';
COMMENT ON TABLE resumes IS 'Stores synthetic resumes for AI agent candidates with skills and experience tracking';
COMMENT ON TABLE job_applications IS 'Links resumes to job descriptions and tracks application status through the hiring process';
COMMENT ON TABLE agents IS 'Active roster of hired AI agents with their assigned models and configurations';
COMMENT ON TABLE tasks IS 'Task management with dependency tracking and cost estimation';
COMMENT ON TABLE task_assignments IS 'Links agents to tasks with capability scoring and cost tracking';
COMMENT ON TABLE model_catalog IS 'Catalog of available AI models with cost and capability information';
COMMENT ON TABLE execution_costs IS 'Detailed tracking of model execution costs per agent and task';
COMMENT ON TABLE task_prompts IS 'Template prompts for different types of task execution';
COMMENT ON TABLE resume_prompts IS 'Template prompts for generating agent personas and decision-making styles';
COMMENT ON TABLE audit_logs IS 'Comprehensive audit trail of all system activities and changes';
