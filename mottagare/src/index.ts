import { skapaGitHub } from "./github";
import { hantera } from "./hantera";
import { skapaLagring } from "./lagring";

interface Miljo {
  DB: D1Database;
  GITHUB_TOKEN: string;
  GITHUB_REPO: string;
  NYCKEL_GRANS: RateLimit;
  IP_GRANS: RateLimit;
  LAS_GRANS: RateLimit;
}

export default {
  async fetch(req: Request, env: Miljo): Promise<Response> {
    try {
      return await hantera(req, {
        lagring: skapaLagring(env.DB),
        github: skapaGitHub(env.GITHUB_TOKEN, env.GITHUB_REPO),
        // IP (redan avkortad till /64 för IPv6) används bara som nyckel i bindningen och lagras aldrig.
        begransa: async (hash, ip) =>
          (await env.NYCKEL_GRANS.limit({ key: hash })).success && (await env.IP_GRANS.limit({ key: ip })).success,
        begransaLasning: async (hash, ip) => (await env.LAS_GRANS.limit({ key: `${hash}:${ip}` })).success,
        nu: () => new Date(),
        nyttId: () => crypto.randomUUID(),
      });
    } catch {
      // Aldrig felmeddelandet: det kan innehålla förslagets text.
      return new Response(JSON.stringify({ fel: "Något gick fel hos mottagaren. Försök igen senare." }), {
        status: 500,
        headers: { "Content-Type": "application/json; charset=utf-8" },
      });
    }
  },
};
