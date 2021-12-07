CREATE TABLE users(
    id INTEGER,
    username TEXT UNIQUE NOT NULL, 
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    college TEXT,
    class TEXT,
    concentration TEXT,
    daychoice TEXT,
    time TEXT,
    place TEXT,
    PRIMARY KEY(id)
);