-- Create test schema and JIRA tables manually
-- Based on the SQLModel definitions in the api/jira/models/ directory

CREATE SCHEMA IF NOT EXISTS test;

SET search_path TO test;

-- Create EventCode enum type first
CREATE TYPE eventcode AS ENUM (
    'BOARD_CREATE',
    'BOARD_UPDATE', 
    'BOARD_DELETE',
    'COLUMN_CREATE',
    'COLUMN_UPDATE',
    'COLUMN_DELETE', 
    'TICKET_CREATE',
    'TICKET_UPDATE',
    'TICKET_DELETE',
    'TICKET_COMMENT_CREATE',
    'TICKET_COMMENT_UPDATE',
    'TICKET_COMMENT_DELETE'
);

-- Create board table
CREATE TABLE IF NOT EXISTS board (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL
);

-- Create status_column table  
CREATE TABLE IF NOT EXISTS status_column (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    board_id INTEGER NOT NULL REFERENCES board(id),
    "order" INTEGER NOT NULL DEFAULT 0
);

-- Create ticket table
CREATE TABLE IF NOT EXISTS ticket (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    assignee VARCHAR,
    conversation VARCHAR,
    column_id INTEGER NOT NULL REFERENCES status_column(id)
);

-- Create ticketcomment table
CREATE TABLE IF NOT EXISTS ticketcomment (
    id SERIAL PRIMARY KEY,
    content VARCHAR NOT NULL,
    author VARCHAR,
    ticket_id INTEGER NOT NULL REFERENCES ticket(id)
);

-- Create webhook table
CREATE TABLE IF NOT EXISTS webhook (
    id SERIAL PRIMARY KEY,
    url VARCHAR NOT NULL,
    event_code eventcode NOT NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_status_column_board_id ON status_column(board_id);
CREATE INDEX IF NOT EXISTS idx_status_column_order ON status_column("order");
CREATE INDEX IF NOT EXISTS idx_ticket_column_id ON ticket(column_id);
CREATE INDEX IF NOT EXISTS idx_ticketcomment_ticket_id ON ticketcomment(ticket_id);
CREATE INDEX IF NOT EXISTS idx_webhook_event_code ON webhook(event_code);

-- Reset search_path to default
SET search_path TO DEFAULT;
