CREATE TABLE IF NOT EXISTS startups (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    website TEXT,
    description TEXT
);
