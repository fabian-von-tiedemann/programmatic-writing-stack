-- Tak per IP och dag. ip_hash är en HMAC av dag och IP med en hemlig nyckel (IP_SALT); IP:n sparas aldrig.
CREATE TABLE ip_dag (
  ip_hash TEXT PRIMARY KEY,
  dag TEXT NOT NULL,
  antal INTEGER NOT NULL
);
CREATE INDEX ip_dag_dag ON ip_dag (dag);
