-- Metabase initialization script
-- This runs on the first database setup to create Metabase's application database

CREATE DATABASE metabase;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE metabase TO postgres;
GRANT ALL PRIVILEGES ON DATABASE bi_platform TO postgres;
