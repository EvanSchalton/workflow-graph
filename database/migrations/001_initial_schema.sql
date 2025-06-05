-- Initial Database Schema for Agentic Workforce Management API
-- This migration creates all core tables needed for the system

-- HR Management Tables
CREATE TABLE job_descriptions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    required_skills JSONB NOT NULL DEFAULT '[]',
    experience_level VARCHAR(50) NOT NULL CHECK (experience_level IN ('junior', 'mid', 'senior', 'lead', 'expert')),
    department VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    summary TEXT,
    skills JSONB NOT NULL DEFAULT '[]',
    experience JSONB NOT NULL DEFAULT '[]',
    education JSONB NOT NULL DEFAULT '[]',
    performance_history JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE job_applications (
    id SERIAL PRIMARY KEY,
    job_description_id INTEGER NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'applied' CHECK (status IN ('applied', 'interviewing', 'hired', 'rejected')),
    application_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interview_notes TEXT,
    hiring_decision_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_description_id, resume_id)
);

CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE RESTRICT,
    job_description_id INTEGER NOT NULL REFERENCES job_descriptions(id) ON DELETE RESTRICT,
    model_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'terminated')),
    configuration JSONB NOT NULL DEFAULT '{}',
    execution_parameters JSONB NOT NULL DEFAULT '{}',
    performance_metrics JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Task Orchestration Tables
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    jira_task_id VARCHAR(100),
    parent_task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'in_progress', 'blocked', 'completed', 'failed')),
    priority VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    required_skills JSONB NOT NULL DEFAULT '[]',
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    dependencies JSONB NOT NULL DEFAULT '[]',
    blockers JSONB NOT NULL DEFAULT '[]',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    deadline TIMESTAMP WITH TIME ZONE
);

CREATE TABLE task_assignments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'assigned' CHECK (status IN ('assigned', 'accepted', 'in_progress', 'completed', 'failed', 'reassigned')),
    capability_score DECIMAL(5,2) NOT NULL DEFAULT 0.0 CHECK (capability_score >= 0.0 AND capability_score <= 100.0),
    cost_estimate DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    completion_notes TEXT,
    quality_score DECIMAL(5,2) CHECK (quality_score >= 0.0 AND quality_score <= 100.0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(task_id, agent_id, assigned_at)
);

-- Cost Tracking Tables
CREATE TABLE model_catalog (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    provider VARCHAR(50) NOT NULL,
    cost_per_input_token DECIMAL(10,8) NOT NULL,
    cost_per_output_token DECIMAL(10,8) NOT NULL,
    context_limit INTEGER NOT NULL,
    performance_tier VARCHAR(20) NOT NULL CHECK (performance_tier IN ('basic', 'standard', 'premium', 'enterprise')),
    capabilities JSONB NOT NULL DEFAULT '[]',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE execution_costs (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    model_name VARCHAR(100) NOT NULL,
    execution_type VARCHAR(50) NOT NULL,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    total_cost DECIMAL(10,6) NOT NULL,
    execution_time_ms INTEGER,
    consensus_round INTEGER DEFAULT 1,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Prompt Management Tables
CREATE TABLE task_prompts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    prompt_template TEXT NOT NULL,
    variables JSONB NOT NULL DEFAULT '[]',
    task_type VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resume_prompts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    prompt_template TEXT NOT NULL,
    variables JSONB NOT NULL DEFAULT '[]',
    persona_type VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit Log Table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    actor_type VARCHAR(50) NOT NULL,
    actor_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance optimization
CREATE INDEX idx_job_descriptions_experience_level ON job_descriptions(experience_level);
CREATE INDEX idx_job_descriptions_department ON job_descriptions(department);
CREATE INDEX idx_job_descriptions_created_at ON job_descriptions(created_at);

CREATE INDEX idx_resumes_skills ON resumes USING GIN(skills);
CREATE INDEX idx_resumes_created_at ON resumes(created_at);

CREATE INDEX idx_job_applications_status ON job_applications(status);
CREATE INDEX idx_job_applications_application_date ON job_applications(application_date);

CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_model_name ON agents(model_name);
CREATE INDEX idx_agents_resume_id ON agents(resume_id);
CREATE INDEX idx_agents_job_description_id ON agents(job_description_id);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_parent_task_id ON tasks(parent_task_id);
CREATE INDEX idx_tasks_jira_task_id ON tasks(jira_task_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_required_skills ON tasks USING GIN(required_skills);

CREATE INDEX idx_task_assignments_status ON task_assignments(status);
CREATE INDEX idx_task_assignments_assigned_at ON task_assignments(assigned_at);
CREATE INDEX idx_task_assignments_task_id ON task_assignments(task_id);
CREATE INDEX idx_task_assignments_agent_id ON task_assignments(agent_id);

CREATE INDEX idx_model_catalog_name ON model_catalog(name);
CREATE INDEX idx_model_catalog_provider ON model_catalog(provider);
CREATE INDEX idx_model_catalog_is_active ON model_catalog(is_active);
CREATE INDEX idx_model_catalog_performance_tier ON model_catalog(performance_tier);

CREATE INDEX idx_execution_costs_agent_id ON execution_costs(agent_id);
CREATE INDEX idx_execution_costs_task_id ON execution_costs(task_id);
CREATE INDEX idx_execution_costs_model_name ON execution_costs(model_name);
CREATE INDEX idx_execution_costs_created_at ON execution_costs(created_at);
CREATE INDEX idx_execution_costs_execution_type ON execution_costs(execution_type);

CREATE INDEX idx_task_prompts_task_type ON task_prompts(task_type);
CREATE INDEX idx_task_prompts_is_active ON task_prompts(is_active);
CREATE INDEX idx_task_prompts_name ON task_prompts(name);

CREATE INDEX idx_resume_prompts_persona_type ON resume_prompts(persona_type);
CREATE INDEX idx_resume_prompts_is_active ON resume_prompts(is_active);
CREATE INDEX idx_resume_prompts_name ON resume_prompts(name);

CREATE INDEX idx_audit_logs_entity_type_id ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_actor_type_id ON audit_logs(actor_type, actor_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Add updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at columns
CREATE TRIGGER update_job_descriptions_updated_at BEFORE UPDATE ON job_descriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_resumes_updated_at BEFORE UPDATE ON resumes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_job_applications_updated_at BEFORE UPDATE ON job_applications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_task_assignments_updated_at BEFORE UPDATE ON task_assignments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_model_catalog_updated_at BEFORE UPDATE ON model_catalog FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_task_prompts_updated_at BEFORE UPDATE ON task_prompts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_resume_prompts_updated_at BEFORE UPDATE ON resume_prompts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
