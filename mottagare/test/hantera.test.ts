import { describe, expect, it } from "vitest";
import { hantera, ipNyckel } from "../src/hantera";
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
    },
    github: {
      skapaIssue: async (rubrik, text, etiketter) => {
        skapade.push({ rubrik, text, etiketter });
        const nummer = 100 + skapade.length;
        issues.set(nummer, { nummer, rubrik, oppen: true, etiketter });
        return nummer;
      },
      hamtaIssue: async (n) => issues.get(n)!,
      hamtaSvar: async (n) => svar.get(n) ?? null,
    },
    begransa: async (_h, ip) => (begransadeIp.push(ip), tillat),
    begransaLasning: async () => tillatLasning,
    nu: () => new Date("2026-10-03T12:00:00Z"),
    nyttId: () => `id-${rader.length + 1}`,
    ...over,
  };
  return { d, rader, skapade, issues, svar, sparrade, begransadeIp, stoppa: () => (tillat = false), stoppaLasning: () => (tillatLasning = false) };
}

const post = (kropp: unknown, nyckel = NYCKEL) =>
  new Request(URL_, {
    method: "POST",
    headers: { Authorization: `Bearer ${nyckel}`, "Content-Type": "application/json", "CF-Connecting-IP": "203.0.113.7" },
    body: typeof kropp === "string" ? kropp : JSON.stringify(kropp),
  });
const get = (nyckel = NYCKEL) => new Request(URL_, { headers: { Authorization: `Bearer ${nyckel}` } });

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
    expect(issue.etiketter).toEqual(["forslag", "typ:problem", "version:2.0.0"]);
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

  it("GitHub-fel sparar inget", async () => {
    const f = fejk();
    f.d.github.skapaIssue = async () => {
      throw new Error("GitHub 500");
    };
    expect((await hantera(post(GILTIG), f.d)).status).toBe(502);
    expect(f.rader).toHaveLength(0);
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
  });

  it("stoppar för tät läsning", async () => {
    const f = fejk();
    f.stoppaLasning();
    expect((await hantera(get(), f.d)).status).toBe(429);
  });

  it("ett fel på en rad förstör inte listan", async () => {
    const f = fejk();
    for (let i = 0; i < 3; i++) await hantera(post(GILTIG), f.d);
    f.issues.set(102, { ...f.issues.get(102)!, etiketter: ["forslag", "status:planerad"] });
    const ordinarie = f.d.github.hamtaIssue;
    f.d.github.hamtaIssue = async (n) => {
      if (n === 101) throw new Error("GitHub 500");
      return ordinarie(n);
    };
    const res = await hantera(get(), f.d);
    expect(res.status).toBe(200);
    const lista = (await res.json()) as { issue: number; rubrik: string; status: string; version: string | null; svar: string | null }[];
    const per = Object.fromEntries(lista.map((s) => [s.issue, s]));
    expect(lista).toHaveLength(3);
    expect(per[101]).toMatchObject({ rubrik: "", status: "mottaget", version: null, svar: null });
    expect(per[102].status).toBe("planerat");
    expect(per[103].rubrik).toBe("Det var krångligt 😅");
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
