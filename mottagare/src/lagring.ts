import type { Lagring } from "./typer";

export function skapaLagring(db: D1Database): Lagring {
  return {
    async arSparrad(h) {
      return (await db.prepare("SELECT 1 FROM sparr WHERE nyckel_hash = ?").bind(h).first()) !== null;
    },
    async antalSedan(h, sedan) {
      const r = await db.prepare("SELECT COUNT(*) AS n FROM forslag WHERE nyckel_hash = ? AND skapad >= ?").bind(h, sedan).first<{ n: number }>();
      return r?.n ?? 0;
    },
    async antalTotaltSedan(sedan) {
      const r = await db.prepare("SELECT COUNT(*) AS n FROM forslag WHERE skapad >= ?").bind(sedan).first<{ n: number }>();
      return r?.n ?? 0;
    },
    async spara(r) {
      await db.prepare("INSERT INTO forslag (id, nyckel_hash, issue, skapad) VALUES (?, ?, ?, ?)").bind(r.id, r.nyckelHash, r.issue, r.skapad).run();
    },
    async lista(h, max) {
      const { results } = await db
        .prepare("SELECT id, issue, skapad FROM forslag WHERE nyckel_hash = ? ORDER BY skapad DESC LIMIT ?")
        .bind(h, max)
        .all<{ id: string; issue: number; skapad: string }>();
      return results;
    },
    async antalIpIdag(ipHash, dag) {
      const r = await db.prepare("SELECT antal FROM ip_dag WHERE ip_hash = ? AND dag = ?").bind(ipHash, dag).first<{ antal: number }>();
      return r?.antal ?? 0;
    },
    async raknaIp(ipHash, dag) {
      // Gamla dagar behövs inte; städas bort i förbifarten.
      await db.prepare("DELETE FROM ip_dag WHERE dag < ?").bind(dag).run();
      await db
        .prepare("INSERT INTO ip_dag (ip_hash, dag, antal) VALUES (?, ?, 1) ON CONFLICT(ip_hash) DO UPDATE SET antal = antal + 1")
        .bind(ipHash, dag)
        .run();
    },
  };
}
