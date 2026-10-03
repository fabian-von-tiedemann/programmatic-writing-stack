import { afterEach, describe, expect, it, vi } from "vitest";
import { hmacHex, sha256 } from "../src/hantera";
import worker from "../src/index";

const NYCKEL = "a".repeat(43);
const URL_ = "https://mottagare.test/v1/forslag";
const GILTIG = { typ: "problem", text: "Hej", sammanhang: "", version: "2.0.0", lage: "", roll: "" };

function fejkMiljo(over: { las?: boolean; lasIp?: boolean; dbFel?: boolean } = {}) {
  const bindningar: { sql: string; args: unknown[] }[] = [];
  const nycklar: Record<string, string[]> = { NYCKEL_GRANS: [], IP_GRANS: [], LAS_GRANS: [], LAS_IP_GRANS: [] };
  const grans = (namn: string, ok = true) => ({ limit: async ({ key }: { key: string }) => (nycklar[namn].push(key), { success: ok }) });
  const DB = {
    prepare(sql: string) {
      if (over.dbFel) throw new Error("hemlig text ur förslaget");
      const stmt = {
        bind: (...args: unknown[]) => (bindningar.push({ sql, args }), stmt),
        first: async () => null,
        all: async () => ({ results: [] }),
        run: async () => ({}),
      };
      return stmt;
    },
  };
  const env = {
    DB,
    GITHUB_TOKEN: "token",
    GITHUB_REPO: "o/r",
    IP_SALT: "salt",
    NYCKEL_GRANS: grans("NYCKEL_GRANS"),
    IP_GRANS: grans("IP_GRANS"),
    LAS_GRANS: grans("LAS_GRANS", over.las ?? true),
    LAS_IP_GRANS: grans("LAS_IP_GRANS", over.lasIp ?? true),
  };
  return { env: env as unknown as Parameters<typeof worker.fetch>[1], bindningar, nycklar };
}

const get = () => new Request(URL_, { headers: { Authorization: `Bearer ${NYCKEL}`, "CF-Connecting-IP": "2001:db8::1" } });

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("worker", () => {
  it("GET begränsas per nyckel och per IP var för sig", async () => {
    const m = fejkMiljo();
    expect((await worker.fetch(get(), m.env)).status).toBe(200);
    expect(m.nycklar.LAS_GRANS).toEqual([await sha256(NYCKEL)]);
    expect(m.nycklar.LAS_IP_GRANS).toEqual(["2001:db8:0:0"]);
  });

  it.each([
    [{ las: false }],
    [{ lasIp: false }],
  ])("GET ger 429 när en gräns slår till (%o)", async (over) => {
    const m = fejkMiljo(over);
    expect((await worker.fetch(get(), m.env)).status).toBe(429);
  });

  it("IP-taget räknas på en HMAC av dag och IP, aldrig IP:n själv", async () => {
    const m = fejkMiljo();
    vi.stubGlobal("fetch", async () => new Response(JSON.stringify({ number: 5 }), { status: 201 }));
    const req = new Request(URL_, {
      method: "POST",
      headers: { Authorization: `Bearer ${NYCKEL}`, "CF-Connecting-IP": "203.0.113.7" },
      body: JSON.stringify(GILTIG),
    });
    expect((await worker.fetch(req, m.env)).status).toBe(201);
    const dag = new Date().toISOString().slice(0, 10);
    const vantad = await hmacHex("salt", `${dag}:203.0.113.7`);
    const ipRader = m.bindningar.filter((b) => b.sql.includes("ip_dag"));
    expect(ipRader.some((b) => b.args.includes(vantad))).toBe(true);
    expect(ipRader.some((b) => b.sql.startsWith("INSERT") && b.sql.includes("ON CONFLICT"))).toBe(true);
    expect(JSON.stringify(m.bindningar)).not.toContain("203.0.113.7");
  });

  it("oväntade fel loggar bara felets namn", async () => {
    const logg = vi.spyOn(console, "error").mockImplementation(() => {});
    const m = fejkMiljo({ dbFel: true });
    const res = await worker.fetch(get(), m.env);
    expect(res.status).toBe(500);
    expect(logg.mock.calls).toEqual([["Error"]]);
  });
});
