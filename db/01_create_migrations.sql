CREATE TABLE deployments (
    id TEXT PRIMARY KEY,
    service TEXT NOT NULL,
    env TEXT NOT NULL,
    image TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);