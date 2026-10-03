import { TYPER, type Forslag, type Typ } from "./typer";

export const MAX_KROPP = 16 * 1024;
const FALT = ["typ", "text", "sammanhang", "version", "lage", "roll"];
const MAX: Record<string, number> = { text: 4000, sammanhang: 2000, lage: 200, roll: 40, version: 20 };

export type Resultat = { ok: true; forslag: Forslag } | { ok: false; fel: string[] };

const text = (v: unknown): string => (typeof v === "string" ? v.trim() : "");

// Längd räknas i tecken (kodpunkter), som i klienten, så att en emoji är ett tecken.
const langd = (s: string): number => [...s].length;

export function validera(data: unknown): Resultat {
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    return { ok: false, fel: ["Förslaget ska vara ett JSON-objekt."] };
  }
  const obj = data as Record<string, unknown>;
  const fel: string[] = [];
  for (const k of Object.keys(obj)) if (!FALT.includes(k)) fel.push(`Okänt fält: ${k}.`);
  if (typeof obj.typ !== "string" || !(TYPER as readonly string[]).includes(obj.typ)) {
    fel.push(`typ måste vara en av ${TYPER.join(", ")}.`);
  }
  for (const k of Object.keys(MAX)) {
    const v = obj[k];
    if (v !== undefined && typeof v !== "string") fel.push(`${k} måste vara text.`);
    else if (typeof v === "string" && langd(v) > MAX[k]) fel.push(`${k} får vara högst ${MAX[k]} tecken.`);
  }
  if (text(obj.text) === "") fel.push("text får inte vara tom.");
  if (typeof obj.version !== "string" || !/^\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(obj.version)) fel.push("version måste se ut som 2.0.0.");
  if (fel.length > 0) return { ok: false, fel };
  return {
    ok: true,
    forslag: {
      typ: obj.typ as Typ,
      text: text(obj.text),
      sammanhang: text(obj.sammanhang),
      version: obj.version as string,
      lage: text(obj.lage),
      roll: text(obj.roll),
    },
  };
}

export function nyckelFranHuvud(huvud: string | null): string | null {
  const m = /^Bearer ([A-Za-z0-9_-]{32,128})$/.exec(huvud ?? "");
  return m ? m[1] : null;
}
