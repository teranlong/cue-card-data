CREATE TABLE IF NOT EXISTS cards (
    id TEXT,
    url TEXT NOT NULL,
    name TEXT NOT NULL,
    album TEXT,
    collection TEXT,
    type TEXT,
    rarity TEXT,
    release_date TEXT,
    energy INTEGER,
    power INTEGER,
    ppe DOUBLE PRECISION,
    ability_name TEXT,
    ability_description TEXT,
    tags TEXT
);

CREATE TEMP TABLE cards_raw (
    url TEXT,
    name TEXT,
    album TEXT,
    collection TEXT,
    id TEXT,
    type TEXT,
    rarity TEXT,
    release_date TEXT,
    energy TEXT,
    power TEXT,
    ppe TEXT,
    ability_name TEXT,
    ability_description TEXT,
    tags TEXT
);

COPY cards_raw (
    url,
    name,
    album,
    collection,
    id,
    type,
    rarity,
    release_date,
    energy,
    power,
    ppe,
    ability_name,
    ability_description,
    tags
)
FROM '/docker-entrypoint-initdb.d/cards_v1.tsv'
WITH (
    FORMAT csv,
    DELIMITER E'\t',
    NULL '',
    HEADER true
);

TRUNCATE TABLE cards;

INSERT INTO cards (
    id,
    url,
    name,
    album,
    collection,
    type,
    rarity,
    release_date,
    energy,
    power,
    ppe,
    ability_name,
    ability_description,
    tags
)
SELECT
    NULLIF(id, ''),
    url,
    name,
    album,
    collection,
    type,
    rarity,
    release_date,
    NULLIF(NULLIF(NULLIF(energy, ''), 'N/A'), 'None')::INTEGER,
    NULLIF(NULLIF(NULLIF(power, ''), 'N/A'), 'None')::INTEGER,
    NULLIF(NULLIF(NULLIF(ppe, ''), 'N/A'), 'None')::DOUBLE PRECISION,
    ability_name,
    ability_description,
    tags
FROM cards_raw;
