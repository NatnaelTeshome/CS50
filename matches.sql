CREATE TABLE matches(
    id INTEGER,
    match_id INTEGER,
    FOREIGN KEY(match_id) REFERENCES users(id)
);