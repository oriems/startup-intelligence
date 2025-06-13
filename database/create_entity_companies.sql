DROP TABLE IF EXISTS entity__companies;

CREATE TABLE entity__companies (
    id SERIAL PRIMARY KEY,
    name TEXT,
    homepage TEXT,
    description TEXT,
    hq_location TEXT,
    industry_tags TEXT[],
    last_enriched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
