# Database Migrations

This directory contains the database migration system for the Agentic Workforce Management API.

## Overview

The migration system creates all the core tables needed for the agentic workforce management system:

- **HR Management**: `job_descriptions`, `resumes`, `job_applications`, `agents`
- **Task Orchestration**: `tasks`, `task_assignments`  
- **Cost Tracking**: `model_catalog`, `execution_costs`
- **Prompt Management**: `task_prompts`, `resume_prompts`
- **Audit Trail**: `audit_logs`

## Migration Files

1. **001_initial_schema.sql** - Creates all core tables with relationships, constraints, and basic indexes
2. **002_add_audit_tables.sql** - Adds additional constraints, business rules, and audit enhancements
3. **003_add_indexes.sql** - Performance optimization indexes, materialized views, and utility functions

## Usage

### Install Dependencies

```bash
cd database
pip install -r requirements.txt
```

### Run All Pending Migrations

```bash
python migrate.py
```

### Check Migration Status

```bash
python migrate.py status
```

### Test Migration System

```bash
python test_migrations.py
```

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (default: `postgresql://jira:jira@docker.lan:5432/postgres`)

## Key Features

### Database Schema

- **Proper foreign key relationships** between all entities
- **JSON fields** for flexible data storage (skills, experience, metadata)
- **Enumerated values** for status fields with validation
- **Timestamp tracking** with automatic `updated_at` triggers
- **Cost validation** to ensure positive values and reasonable ranges

### Performance Optimizations

- **Comprehensive indexing** for common query patterns
- **Partial indexes** for filtered queries (active records, recent data)
- **Full-text search** indexes for text fields
- **Materialized views** for expensive aggregations
- **Composite indexes** for complex joins

### Business Logic

- **Automatic task status updates** when assignments complete
- **Agent status validation** to prevent terminating agents with active work
- **Dependency tracking** with circular reference prevention
- **Cost attribution** linking executions to specific tasks and agents

### Audit and Monitoring

- **Comprehensive audit logs** for all system activities
- **Performance metrics** tracking for agents and tasks
- **Cost summaries** with daily aggregations
- **Utilization calculations** for agent performance monitoring

## Database Schema Details

### Core Relationships

```
job_descriptions 1 -> N job_applications N <- 1 resumes
job_descriptions 1 -> N agents N <- 1 resumes
agents 1 -> N task_assignments N <- 1 tasks
tasks 1 -> N tasks (parent_task_id for subtasks)
agents 1 -> N execution_costs
tasks 1 -> N execution_costs
```

### Key Constraints

- Only one active agent per job description
- Tasks cannot be self-referencing parents
- All costs must be positive
- JSON fields must have proper array structure
- Agents cannot be terminated with active assignments

### Views and Functions

- `active_agents_with_jobs` - Join agents with their job details
- `task_status_summary` - Task completion statistics
- `cost_summary_by_agent` - Agent cost analysis
- `daily_cost_summary` - Materialized view for cost reporting
- `calculate_agent_utilization()` - Function for utilization metrics

## Migration Tracking

The system uses a `schema_migrations` table to track which migrations have been executed. This prevents duplicate execution and allows for safe incremental updates.

## Testing

The test script verifies:

- ✅ Table creation and structure
- ✅ Constraint enforcement (ENUMs, JSON, foreign keys, positive values)
- ✅ Index creation
- ✅ View and function creation
- ✅ Migration tracking system

## Future Migrations

To add new migrations:

1. Create a new SQL file with format `XXX_description.sql`
2. Use sequential numbering (004, 005, etc.)
3. Test thoroughly before deploying
4. Document any breaking changes

## Rollback Strategy

Currently, the system does not support automatic rollbacks. For schema changes:

1. Create backup before migration
2. Test migrations on staging environment
3. Plan manual rollback procedures if needed
4. Consider creating explicit rollback migration files for complex changes
