import { skapaGitHub } from "./github";
import { hantera } from "./hantera";
import { skapaLagring } from "./lagring";

interface Miljo {
  DB: D1Database;
  GITHUB_TOKEN: string;
  GITHUB_REPO: string;
  NYCKEL_GRANS: RateLimit;
  IP_GRANS: RateLimit;
}

export default {
  async fetch(req: Request, env: Miljo): Promise<Response> {
    return hantera(req, {
      lagring: skapaLagring(env.DB),
      github: skapaGitHub(env.GITHUB_TOKEN, env.GITHUB_REPO),
      // IP används bara som nyckel i bindningen och lagras aldrig.
      begransa: async (hash, ip) =>
        (await env.NYCKEL_GRANS.limit({ key: hash })).success && (await env.IP_GRANS.limit({ key: ip })).success,
      nu: () => new Date(),
      nyttId: () => crypto.randomUUID(),
    });
  },
};
