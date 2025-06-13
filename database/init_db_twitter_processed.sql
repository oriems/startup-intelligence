-- init_db_twitter_processed.sql

-- CREATE TABLE IF NOT EXISTS twitter_processed (
--     id SERIAL PRIMARY KEY,
--     tweet_id VARCHAR NOT NULL REFERENCES twitter_raw(tweet_id) ON DELETE CASCADE,
--     company_name TEXT,
--     round_amount NUMERIC,
--     currency TEXT,
--     round_type TEXT,
--     date DATE,
--     investors TEXT[],  -- stored as array of names
--     location TEXT,
--     source_url TEXT,
--     confidence NUMERIC,
--     notes TEXT,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );


CREATE TABLE IF NOT EXISTS twitter_processed (
    tweet_id TEXT PRIMARY KEY,
    company_name TEXT,
    round_amount TEXT,
    currency TEXT,
    round_type TEXT,
    date TEXT,  -- Use text instead of DATE for flexibility
    investors TEXT,  -- Can store JSON as a string or comma-separated names
    location TEXT,
    source_url TEXT,
    confidence TEXT,  -- If provided by OpenAI
    notes TEXT  -- For logging or errors
);