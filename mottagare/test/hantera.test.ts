import { afterEach, describe, expect, it, vi } from "vitest";
import { GitHubFel } from "../src/github";
import { hantera, hmacHex, ipNyckel } from "../src/hantera";
import type { Beroenden, Issue, Rad } from "../src/typer";
import { validera } from "../src/validera";

const NYCKEL = "a".repeat(43);
const URL_ = "https://mottagare.test/v1/forslag";
const GILTIG = { typ: "problem", text: "Det var krångligt 😅\nmed betygen", sammanhang: "I granskningen.", version: "2.0.0", lage: "kapitel 3: revision", roll: "sprakgranskare" };

function fejk(over: Partial<Beroenden> = {}) {
  const rader: Rad[] = [];
  const skapade: { rubrik: string; text: string; etiketter: string[] }[] = [];
  const issues = new Map<number, Issue>();
  const svar = new Map<number, string>();
  const sparrade = new Set<string>();
  const ipDag = new Map<string, { dag: string; antal: number }>();
  const hamtningar: number[][] = [];
  let tillat = true;
  let tillatLasning = true;
  const begransadeIp: string[] = [];
  const d: Beroenden = {
    lagring: {
      arSparrad: async (h) => sparrade.has(h),
      antalSedan: async (h, sedan) => rader.filter((r) => r.nyckelHash === h && r.skapad >= sedan).length,
      antalTotaltSedan: async (sedan) => rader.filter((r) => r.skapad >= sedan).length,
      spara: async (r) => void rader.push(r),
      lista: async (h, max) => rader.filter((r) => r.nyckelHash === h).slice(0, max).map(({ id, issue, skapad }) => ({ id, issue, skapad })),
      antalIpIdag: async (ipHash, dag) => (ipDag.get(ipHash)?.dag === dag ? ipDag.get(ipHash)!.antal : 0),
      raknaIp: async (ipHash, dag) => void ipDag.set(ipHash, { dag, antal: (ipDag.get(ipHash)?.antal ?? 0) + 1 }),
    },
    github: {
      skapaIssue: async (rubrik, text, etiketter) => {
        skapade.push({ rubrik, text, etiketter });
        const nummer = 100 + skapade.length;
        issues.set(nummer, { nummer, rubrik, oppen: true, etiketter });
        return nummer;
      },
      hamtaManga: async (nummer) => {
        hamtningar.push(nummer);
        return new Map(nummer.map((n) => [n, issues.has(n) ? { issue: issues.get(n)!, svar: svar.get(n) ?? null } : null]));
      },
    },
    begransa: async (_h, ip) => (begransadeIp.push(ip), tillat),
    begransaLasning: async () => tillatLasning,
    ipHash: async (ip, dag) => `${dag}:${ip}`,
    nu: () => new Date("2026-10-03T12:00:00Z"),
    nyttId: () => `id-${rader.length + 1}`,
    ...over,
  };
  return { d, rader, skapade, issues, svar, sparrade, begransadeIp, ipDag, hamtningar, stoppa: () => (tillat = false), stoppaLasning: () => (tillatLasning = false) };
}

const post = (kropp: unknown, nyckel = NYCKEL, ip = "203.0.113.7") =>
  new Request(URL_, {
    method: "POST",
    headers: { Authorization: `Bearer ${nyckel}`, "Content-Type": "application/json", "CF-Connecting-IP": ip },
    body: typeof kropp === "string" ? kropp : JSON.stringify(kropp),
  });
const get = (nyckel = NYCKEL) => new Request(URL_, { headers: { Authorization: `Bearer ${nyckel}` } });

afterEach(() => vi.restoreAllMocks());

describe("POST /v1/forslag", () => {
  it("skapar ett issue och sparar bara en hash av nyckeln", async () => {
    const f = fejk();
    const res = await hantera(post(GILTIG), f.d);
    expect(res.status).toBe(201);
    expect(await res.json()).toEqual({ id: "id-1", issue: 101 });
    const issue = f.skapade[0];
    expect(issue.rubrik).toBe("Det var krångligt 😅");
    expect(issue.text).toContain("Det var krångligt 😅\nmed betygen");
    expect(issue.text).toContain("I granskningen.");
    expect(issue.text).toContain("kapitel 3: revision");
    expect(issue.etiketter).toEqual(["forslag", "typ:problem"]);
    expect(issue.text).toContain("- Version: 2.0.0");
    expect(f.rader[0].nyckelHash).toMatch(/^[0-9a-f]{64}$/);
    expect(f.rader[0].nyckelHash).not.toBe(NYCKEL);
    expect(issue.text).not.toContain(NYCKEL);
    expect(issue.text).not.toContain(f.rader[0].nyckelHash);
    expect(issue.text).not.toContain("203.0.113.7");
  });

  it("pingar ingen på GitHub", async () => {
    const f = fejk();
    await hantera(post({ ...GILTIG, text: "Fråga @someone och @org/team" }), f.d);
    expect(f.skapade[0].text).toContain("```\nFråga @someone och @org/team\n```");
    expect(f.skapade[0].rubrik).not.toMatch(/@[A-Za-z]/);
  });

  it("ett ``` i texten kan inte stänga kodblocket", async () => {
    const f = fejk();
    await hantera(post({ ...GILTIG, text: "före\n```\n# Rubrik ![bild](x)\n```\nefter", sammanhang: "````\nfyra" }), f.d);
    const t = f.skapade[0].text;
    expect(t).toContain("````\nföre\n```\n# Rubrik ![bild](x)\n```\nefter\n````");
    expect(t).toContain("`````\n````\nfyra\n`````");
  });

  it("rader och styrtecken i läge och roll blir inga nya markdownrader", async () => {
    const f = fejk();
    await hantera(post({ ...GILTIG, lage: "a\n- Typ: `hack`\u202E\u0007 b", roll: "x\r\n## Rubrik" }), f.d);
    const rader = f.skapade[0].text.split("\n");
    expect(rader.filter((r) => r.startsWith("- "))).toHaveLength(4);
    expect(rader).toContain("- Läge: `a - Typ: hack b`");
    expect(rader).toContain("- Roll: `x ## Rubrik`");
    expect(f.skapade[0].text).not.toMatch(/[\u202A-\u202E\u2066-\u2069\u0007]/);
  });

  it("rubriken blir en rad utan styrtecken", async () => {
    const f = fejk();
    await hantera(post({ ...GILTIG, text: "Hej\u202E\u0007   du\n@alla" }), f.d);
    expect(f.skapade[0].rubrik).toBe("Hej du");
  });

  it("tom rubrik efter rensning blir Förslag", async () => {
    const f = fejk();
    expect((await hantera(post({ ...GILTIG, text: "\u202E\nmer text" }), f.d)).status).toBe(201);
    expect(f.skapade[0].rubrik).toBe("Förslag");
  });

  it("kortar långa rubriker", async () => {
    const f = fejk();
    await hantera(post({ ...GILTIG, text: "x".repeat(200) }), f.d);
    expect(f.skapade[0].rubrik.length).toBeLessThanOrEqual(70);
  });

  it.each([
    [{ ...GILTIG, okant: 1 }, "Okänt fält: okant."],
    [{ ...GILTIG, typ: "klagomal" }, "typ måste vara"],
    [{ ...GILTIG, text: "a".repeat(4001) }, "högst 4000"],
    [{ ...GILTIG, text: "  " }, "text får inte vara tom"],
    [{ ...GILTIG, version: "senaste" }, "version måste"],
    [{ ...GILTIG, version: "1000.0.0" }, "version måste"],
    ["{inte json", "inte giltig JSON"],
    [[1, 2], "JSON-objekt"],
  ])("avvisar ogiltiga förslag", async (kropp, fel) => {
    const f = fejk();
    const res = await hantera(post(kropp), f.d);
    expect(res.status).toBe(400);
    expect(((await res.json()) as { fel: string }).fel).toContain(fel);
    expect(f.skapade).toHaveLength(0);
  });

  it("räknar längd i tecken, inte UTF-16-enheter", async () => {
    const f = fejk();
    const res = await hantera(post({ ...GILTIG, text: "😅".repeat(2000) }), f.d);
    expect(res.status).toBe(201);
    const v = validera({ ...GILTIG, text: "😅".repeat(4000) });
    expect(v.ok).toBe(true);
    const f2 = fejk();
    expect((await hantera(post({ ...GILTIG, text: "a".repeat(4001) }), f2.d)).status).toBe(400);
  });

  it("avvisar för stora anrop", async () => {
    const f = fejk();
    const res = await hantera(post({ ...GILTIG, sammanhang: "å".repeat(9000) }), f.d);
    expect(res.status).toBe(413);
  });

  it("avvisar på Content-Length innan kroppen läses", async () => {
    const f = fejk();
    const req = new Request(URL_, {
      method: "POST",
      headers: { Authorization: `Bearer ${NYCKEL}`, "Content-Length": String(16 * 1024 + 1) },
      body: "{}",
    });
    expect((await hantera(req, f.d)).status).toBe(413);
  });

  it("kräver nyckel", async () => {
    const f = fejk();
    expect((await hantera(post(GILTIG, "kort"), f.d)).status).toBe(401);
    expect((await hantera(new Request(URL_, { method: "POST", body: "{}" }), f.d)).status).toBe(401);
  });

  it("stoppar skurar", async () => {
    const f = fejk();
    f.stoppa();
    expect((await hantera(post(GILTIG), f.d)).status).toBe(429);
  });

  it("högst fem per timme per nyckel", async () => {
    const f = fejk();
    for (let i = 0; i < 5; i++) expect((await hantera(post(GILTIG), f.d)).status).toBe(201);
    const res = await hantera(post(GILTIG), f.d);
    expect(res.status).toBe(429);
  });

  it("globalt tak: nya nycklar kommer inte förbi", async () => {
    const f = fejk();
    for (let i = 0; i < 60; i++) f.rader.push({ id: `x${i}`, nyckelHash: `h${i}`, issue: i, skapad: "2026-10-03T11:30:00.000Z" });
    const res = await hantera(post(GILTIG, "c".repeat(43)), f.d);
    expect(res.status).toBe(429);
    expect(await res.json()).toEqual({ fel: "Mottagaren tar inte emot fler förslag just nu. Försök igen om en stund." });
    expect(f.skapade).toHaveLength(0);
  });

  it("globalt tak räknar bara senaste timmen", async () => {
    const f = fejk();
    for (let i = 0; i < 60; i++) f.rader.push({ id: `x${i}`, nyckelHash: `h${i}`, issue: i, skapad: "2026-10-03T10:30:00.000Z" });
    expect((await hantera(post(GILTIG), f.d)).status).toBe(201);
  });

  it("begränsar IP på /64-prefixet", async () => {
    const f = fejk();
    const req = new Request(URL_, {
      method: "POST",
      headers: { Authorization: `Bearer ${NYCKEL}`, "CF-Connecting-IP": "2001:db8::1" },
      body: JSON.stringify(GILTIG),
    });
    await hantera(req, f.d);
    expect(f.begransadeIp).toEqual(["2001:db8:0:0"]);
  });

  it("spärrade nycklar", async () => {
    const f = fejk();
    const hash = await sha256hex(NYCKEL);
    f.sparrade.add(hash);
    expect((await hantera(post(GILTIG), f.d)).status).toBe(403);
  });

  it("GitHub-fel sparar inget och loggar bara statuskoden", async () => {
    const f = fejk();
    const logg = vi.spyOn(console, "error").mockImplementation(() => {});
    f.d.github.skapaIssue = async () => {
      throw new GitHubFel(401);
    };
    expect((await hantera(post(GILTIG), f.d)).status).toBe(502);
    expect(f.rader).toHaveLength(0);
    expect(f.ipDag.size).toBe(0);
    expect(logg.mock.calls).toEqual([["GitHub 401"]]);
  });

  it("högst 30 per dag från samma IP, även med olika nycklar", async () => {
    const f = fejk();
    for (let i = 0; i < 30; i++) {
      const nyckel = `k${String(i).padStart(2, "0")}`.padEnd(43, "x");
      expect((await hantera(post(GILTIG, nyckel), f.d)).status).toBe(201);
    }
    const res = await hantera(post(GILTIG, "y".repeat(43)), f.d);
    expect(res.status).toBe(429);
    expect(await res.json()).toEqual({ fel: "För många förslag på kort tid. Vänta en stund och försök igen." });
    expect(f.skapade).toHaveLength(30);
    expect((await hantera(post(GILTIG, "z".repeat(43), "198.51.100.9"), f.d)).status).toBe(201);
  });

  it("räknar IP per dag med hash av dag och /64-prefix", async () => {
    const f = fejk();
    await hantera(post(GILTIG, NYCKEL, "2001:db8::1"), f.d);
    expect([...f.ipDag.entries()]).toEqual([["2026-10-03:2001:db8:0:0", { dag: "2026-10-03", antal: 1 }]]);
  });

  it("ett avvisat förslag räknas inte mot IP-taket", async () => {
    const f = fejk();
    await hantera(post({ ...GILTIG, typ: "klagomal" }), f.d);
    expect(f.ipDag.size).toBe(0);
  });
});

describe("GET /v1/forslag", () => {
  it("visar bara egna förslag med status och svar", async () => {
    const f = fejk();
    for (let i = 0; i < 4; i++) await hantera(post(GILTIG), f.d);
    await hantera(post(GILTIG, "b".repeat(43)), f.d);
    f.issues.set(102, { ...f.issues.get(102)!, etiketter: ["forslag", "status:planerad"] });
    f.issues.set(103, { ...f.issues.get(103)!, etiketter: ["forslag", "infort:2.1.0"], oppen: false });
    f.issues.set(104, { ...f.issues.get(104)!, etiketter: ["forslag", "status:avbojd"], oppen: false });
    f.svar.set(104, "Det passar inte verktyget, men tack!");
    const res = await hantera(get(), f.d);
    expect(res.status).toBe(200);
    const lista = (await res.json()) as { issue: number; status: string; version: string | null; svar: string | null }[];
    const per = Object.fromEntries(lista.map((s) => [s.issue, s]));
    expect(lista).toHaveLength(4);
    expect(per[101].status).toBe("mottaget");
    expect(per[102].status).toBe("planerat");
    expect(per[103]).toMatchObject({ status: "infort", version: "2.1.0" });
    expect(per[104]).toMatchObject({ status: "avbojt", svar: "Det passar inte verktyget, men tack!" });
    // Ett enda anrop till GitHub för hela listan.
    expect(f.hamtningar).toHaveLength(1);
    expect([...f.hamtningar[0]].sort()).toEqual([101, 102, 103, 104]);
  });

  it("utan förslag anropas inte GitHub", async () => {
    const f = fejk();
    const res = await hantera(get(), f.d);
    expect(await res.json()).toEqual([]);
    expect(f.hamtningar).toHaveLength(0);
  });

  it("stoppar för tät läsning", async () => {
    const f = fejk();
    f.stoppaLasning();
    expect((await hantera(get(), f.d)).status).toBe(429);
  });

  it("ett saknat issue blir okänt utan att förstöra listan", async () => {
    const f = fejk();
    for (let i = 0; i < 3; i++) await hantera(post(GILTIG), f.d);
    f.issues.set(102, { ...f.issues.get(102)!, etiketter: ["forslag", "status:planerad"] });
    f.issues.delete(101);
    const res = await hantera(get(), f.d);
    expect(res.status).toBe(200);
    const lista = (await res.json()) as { issue: number; rubrik: string; status: string; version: string | null; svar: string | null }[];
    const per = Object.fromEntries(lista.map((s) => [s.issue, s]));
    expect(lista).toHaveLength(3);
    expect(per[101]).toMatchObject({ rubrik: "", status: "okand", version: null, svar: null });
    expect(per[102].status).toBe("planerat");
    expect(per[103].rubrik).toBe("Det var krångligt 😅");
  });

  it("ger 502 när GitHub inte svarar", async () => {
    const f = fejk();
    const logg = vi.spyOn(console, "error").mockImplementation(() => {});
    await hantera(post(GILTIG), f.d);
    f.d.github.hamtaManga = async () => {
      throw new GitHubFel(503);
    };
    const res = await hantera(get(), f.d);
    expect(res.status).toBe(502);
    expect(logg.mock.calls).toEqual([["GitHub 503"]]);
  });

  it("listar högst 20", async () => {
    const f = fejk();
    let max = 0;
    f.d.lagring.lista = async (_h, m) => ((max = m), []);
    await hantera(get(), f.d);
    expect(max).toBe(20);
  });

  it("okända vägar och metoder", async () => {
    const f = fejk();
    expect((await hantera(new Request("https://mottagare.test/annat"), f.d)).status).toBe(404);
    expect((await hantera(new Request(URL_, { method: "PUT", headers: { Authorization: `Bearer ${NYCKEL}` } }), f.d)).status).toBe(405);
  });
});

async function sha256hex(s: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

describe("hmacHex", () => {
  it("är HMAC-SHA256 i hex", async () => {
    expect(await hmacHex("key", "The quick brown fox jumps over the lazy dog")).toBe(
      "f7bc83f430538424b13298e6aa6fb143ef4d59a14946175997479dbc2d1a3cd8",
    );
  });
});

describe("ipNyckel", () => {
  it.each([
    ["203.0.113.7", "203.0.113.7"],
    ["okand", "okand"],
    ["2001:0db8:85a3:0042:1000:8a2e:0370:7334", "2001:db8:85a3:42"],
    ["2001:db8::1", "2001:db8:0:0"],
    ["2001:db8:1:2:3::9", "2001:db8:1:2"],
    ["::1", "0:0:0:0"],
    ["::ffff:192.0.2.1", "0:0:0:0"],
  ])("%s -> %s", (ip, vantat) => {
    expect(ipNyckel(ip)).toBe(vantat);
  });
});
