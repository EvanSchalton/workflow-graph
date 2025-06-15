-- JIRA Tables Migration
-- This migration creates the JIRA-specific tables that are normally created by SQLModel

-- Create EventCode enum type
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

-- Board table for organizing tickets into boards
CREATE TABLE board (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL
);

-- Status columns for organizing tickets within boards  
CREATE TABLE status_column (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    board_id INTEGER NOT NULL REFERENCES board(id) ON DELETE CASCADE,
    "order" INTEGER NOT NULL DEFAULT 0
);

-- Tickets that belong to status columns
CREATE TABLE ticket (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    assignee VARCHAR,
    conversation VARCHAR,
    column_id INTEGER NOT NULL REFERENCES status_column(id) ON DELETE CASCADE
);

-- Comments on tickets
CREATE TABLE ticketcomment (
    id SERIAL PRIMARY KEY,
    content VARCHAR NOT NULL,
    author VARCHAR,
    ticket_id INTEGER NOT NULL REFERENCES ticket(id) ON DELETE CASCADE
);

-- Webhooks for event notifications
CREATE TABLE webhook (
    id SERIAL PRIMARY KEY,
    url VARCHAR NOT NULL,
    event_code eventcode NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_status_column_board_id ON status_column(board_id);
CREATE INDEX idx_status_column_order ON status_column("order");
CREATE INDEX idx_ticket_column_id ON ticket(column_id);
CREATE INDEX idx_ticketcomment_ticket_id ON ticketcomment(ticket_id);
CREATE INDEX idx_webhook_event_code ON webhook(event_code);
