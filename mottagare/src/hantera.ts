import type { Beroenden, Forslag, ForslagStatus, Issue } from "./typer";
import { MAX_KROPP, nyckelFranHuvud, validera } from "./validera";

const PER_TIMME = 5;
const TOTALT_PER_TIMME = 60;
const MAX_LISTA = 20;

const json = (status: number, data: unknown): Response =>
  new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json; charset=utf-8" } });

export async function sha256(text: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// IPv4 oförändrad; IPv6 blir sina första fyra grupper (/64), så att en hel adressrymd räknas som en.
export function ipNyckel(ip: string): string {
  if (!ip.includes(":")) return ip;
  let adress = ip.split("%")[0].toLowerCase();
  const sista = adress.slice(adress.lastIndexOf(":") + 1);
  if (sista.includes(".")) {
    const o = sista.split(".").map(Number);
    if (o.length !== 4 || o.some((n) => !(n >= 0 && n <= 255))) return ip;
    adress = `${adress.slice(0, adress.lastIndexOf(":") + 1)}${((o[0] << 8) | o[1]).toString(16)}:${((o[2] << 8) | o[3]).toString(16)}`;
  }
  const [fore, efter, ...rest] = adress.split("::");
  if (rest.length > 0) return ip;
  const delar = (s: string | undefined): string[] => (s ? s.split(":") : []);
  const hel = efter === undefined ? delar(fore) : [...delar(fore), ...Array(Math.max(0, 8 - delar(fore).length - delar(efter).length)).fill("0"), ...delar(efter)];
  if (hel.length !== 8 || hel.some((h) => !/^[0-9a-f]{1,4}$/.test(h))) return ip;
  return hel.slice(0, 4).map((h) => parseInt(h, 16).toString(16)).join(":");
}

// Styrtecken och dubbelriktade styrtecken bort, blanka till ett mellanslag.
const rens = (s: string): string => s.replace(/[\p{Cc}‪-‮⁦-⁩]/gu, " ").replace(/\s+/g, " ").trim();

// "@namn" pingar personer på GitHub; ett osynligt tecken (U+200B) efter @ hindrar det. Används bara i rubriken.
const tyst = (s: string): string => s.replace(/@(?=[A-Za-z0-9])/g, "@​");

// Kortas på tecken (kodpunkter), så att en emoji aldrig klyvs mitt i.
function rubrik(text: string): string {
  const forsta = [...tyst(rens(text.split("\n")[0]))];
  return forsta.length > 70 ? `${forsta.slice(0, 69).join("")}…` : forsta.join("");
}

// Kodblock vars staket är längre än alla backtick-följder i värdet; inget inuti tolkas som markdown.
function kodblock(s: string): string {
  const langsta = Math.max(0, ...(s.match(/`+/g) ?? []).map((m) => m.length));
  const staket = "`".repeat(Math.max(3, langsta + 1));
  return `${staket}\n${s}\n${staket}`;
}

const rad = (s: string): string => rens(s).replaceAll("`", "").trim();
const inline = (s: string): string => (rad(s) ? `\`${rad(s)}\`` : "–");

function issueText(f: Forslag): string {
  return [
    "## Förslaget",
    "",
    kodblock(f.text),
    "",
    "## Sammanhang",
    "",
    f.sammanhang ? kodblock(f.sammanhang) : "–",
    "",
    "## Detaljer",
    "",
    `- Typ: ${f.typ}`,
    `- Version: ${f.version}`,
    `- Läge: ${inline(f.lage)}`,
    `- Roll: ${inline(f.roll)}`,
  ].join("\n");
}

function status(issue: Issue): Pick<ForslagStatus, "status" | "version"> {
  const infort = issue.etiketter.find((e) => e.startsWith("infort:"));
  if (infort) return { status: "infort", version: infort.slice("infort:".length) };
  if (issue.etiketter.includes("status:avbojd")) return { status: "avbojt", version: null };
  if (issue.etiketter.includes("status:planerad")) return { status: "planerat", version: null };
  return { status: "mottaget", version: null };
}

export async function hantera(req: Request, d: Beroenden): Promise<Response> {
  if (new URL(req.url).pathname !== "/v1/forslag") return json(404, { fel: "Finns inte." });
  const nyckel = nyckelFranHuvud(req.headers.get("Authorization"));
  if (!nyckel) return json(401, { fel: "Saknar giltig nyckel." });
  const hash = await sha256(nyckel);
  if (req.method === "POST") return taEmot(req, hash, d);
  if (req.method === "GET") return lista(hash, req, d);
  return json(405, { fel: "Metoden stöds inte." });
}

async function taEmot(req: Request, hash: string, d: Beroenden): Promise<Response> {
  const ip = ipNyckel(req.headers.get("CF-Connecting-IP") ?? "okand");
  const forMycket = { fel: "För många förslag på kort tid. Vänta en stund och försök igen." };
  if (!(await d.begransa(hash, ip))) return json(429, forMycket);
  if (await d.lagring.arSparrad(hash)) return json(403, { fel: "Den här nyckeln kan inte skicka förslag." });
  const timmeSedan = new Date(d.nu().getTime() - 3_600_000).toISOString();
  if ((await d.lagring.antalSedan(hash, timmeSedan)) >= PER_TIMME) return json(429, forMycket);
  if ((await d.lagring.antalTotaltSedan(timmeSedan)) >= TOTALT_PER_TIMME) {
    return json(429, { fel: "Mottagaren tar inte emot fler förslag just nu. Försök igen om en stund." });
  }
  if (Number(req.headers.get("Content-Length")) > MAX_KROPP) return json(413, { fel: "Förslaget är för stort." });
  const ra = await req.text();
  if (new TextEncoder().encode(ra).length > MAX_KROPP) return json(413, { fel: "Förslaget är för stort." });
  let data: unknown;
  try {
    data = JSON.parse(ra);
  } catch {
    return json(400, { fel: "Förslaget är inte giltig JSON." });
  }
  const v = validera(data);
  if (!v.ok) return json(400, { fel: v.fel.join(" ") });
  const f = v.forslag;
  let issue: number;
  try {
    issue = await d.github.skapaIssue(rubrik(f.text), issueText(f), ["forslag", `typ:${f.typ}`, `version:${f.version}`]);
  } catch {
    return json(502, { fel: "Kunde inte spara förslaget just nu. Försök igen senare." });
  }
  const id = d.nyttId();
  await d.lagring.spara({ id, nyckelHash: hash, issue, skapad: d.nu().toISOString() });
  return json(201, { id, issue });
}

async function lista(hash: string, req: Request, d: Beroenden): Promise<Response> {
  const ip = ipNyckel(req.headers.get("CF-Connecting-IP") ?? "okand");
  if (!(await d.begransaLasning(hash, ip))) {
    return json(429, { fel: "För många förfrågningar på kort tid. Vänta en stund och försök igen." });
  }
  const rader = await d.lagring.lista(hash, MAX_LISTA);
  const ut: ForslagStatus[] = await Promise.all(
    rader.map(async (r): Promise<ForslagStatus> => {
      try {
        const [issue, svar] = await Promise.all([d.github.hamtaIssue(r.issue), d.github.hamtaSvar(r.issue)]);
        return { id: r.id, issue: r.issue, rubrik: issue.rubrik, skapad: r.skapad, ...status(issue), svar };
      } catch {
        // Ett fel på en rad ska inte stoppa hela listan.
        return { id: r.id, issue: r.issue, rubrik: "", skapad: r.skapad, status: "mottaget", version: null, svar: null };
      }
    }),
  );
  return json(200, ut);
}
