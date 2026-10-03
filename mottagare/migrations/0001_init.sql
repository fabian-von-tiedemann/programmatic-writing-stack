CREATE TABLE forslag (
  id TEXT PRIMARY KEY,
  nyckel_hash TEXT NOT NULL,
  issue INTEGER NOT NULL,
  skapad TEXT NOT NULL
);
CREATE INDEX forslag_nyckel ON forslag (nyckel_hash, skapad);
CREATE TABLE sparr (
  nyckel_hash TEXT PRIMARY KEY,
  skal TEXT NOT NULL DEFAULT ''
);
