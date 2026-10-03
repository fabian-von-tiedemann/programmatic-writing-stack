import type { Beroenden, Forslag, ForslagStatus, Issue } from "./typer";
import { MAX_KROPP, nyckelFranHuvud, validera } from "./validera";

const PER_TIMME = 5;
const MAX_LISTA = 50;

const json = (status: number, data: unknown): Response =>
  new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json; charset=utf-8" } });

export async function sha256(text: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// "@namn" pingar personer på GitHub; ett osynligt tecken (U+200B) efter @ hindrar det.
const tyst = (s: string): string => s.replace(/@(?=[A-Za-z0-9])/g, "@​");

// Kortas på tecken (kodpunkter), så att en emoji aldrig klyvs mitt i.
function rubrik(text: string): string {
  const forsta = [...tyst(text.split("\n")[0].trim())];
  return forsta.length > 70 ? `${forsta.slice(0, 69).join("")}…` : forsta.join("");
}

function issueText(f: Forslag): string {
  return [
    "## Förslaget",
    "",
    tyst(f.text),
    "",
    "## Sammanhang",
    "",
    tyst(f.sammanhang) || "–",
    "",
    "## Detaljer",
    "",
    `- Typ: ${f.typ}`,
    `- Version: ${f.version}`,
    `- Läge: ${tyst(f.lage) || "–"}`,
    `- Roll: ${tyst(f.roll) || "–"}`,
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
  if (req.method === "GET") return lista(hash, d);
  return json(405, { fel: "Metoden stöds inte." });
}

async function taEmot(req: Request, hash: string, d: Beroenden): Promise<Response> {
  const ip = req.headers.get("CF-Connecting-IP") ?? "okand";
  const forMycket = { fel: "För många förslag på kort tid. Vänta en stund och försök igen." };
  if (!(await d.begransa(hash, ip))) return json(429, forMycket);
  if (await d.lagring.arSparrad(hash)) return json(403, { fel: "Den här nyckeln kan inte skicka förslag." });
  const timmeSedan = new Date(d.nu().getTime() - 3_600_000).toISOString();
  if ((await d.lagring.antalSedan(hash, timmeSedan)) >= PER_TIMME) return json(429, forMycket);
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

async function lista(hash: string, d: Beroenden): Promise<Response> {
  const rader = await d.lagring.lista(hash, MAX_LISTA);
  try {
    const ut: ForslagStatus[] = await Promise.all(
      rader.map(async (r) => {
        const [issue, svar] = await Promise.all([d.github.hamtaIssue(r.issue), d.github.hamtaSvar(r.issue)]);
        return { id: r.id, issue: r.issue, rubrik: issue.rubrik, skapad: r.skapad, ...status(issue), svar };
      }),
    );
    return json(200, ut);
  } catch {
    return json(502, { fel: "Kunde inte hämta status just nu. Försök igen senare." });
  }
}
