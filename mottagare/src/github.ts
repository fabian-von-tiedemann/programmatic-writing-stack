import type { GitHub, Issue } from "./typer";

// Meddelandet byggs bara av statuskoden eller en fast text, aldrig av svarets innehåll.
export class GitHubFel extends Error {
  constructor(kod: number | string) {
    super(`GitHub ${kod}`);
    this.name = "GitHubFel";
  }
}

// Det enda som loggas om ett fel: namnet, och statuskoden för GitHub-fel. Aldrig meddelanden
// som kan innehålla förslagets text, huvuden, nyckeln eller tokenen.
export function diagnos(fel: unknown): string {
  if (fel instanceof GitHubFel) return fel.message;
  if (fel instanceof Error) return fel.name;
  return "okänt fel";
}

interface IssueNod {
  number: number;
  title: string;
  state: string;
  labels: { nodes: { name: string }[] };
  comments: { nodes: { body: string }[] };
}

// Ett saknat eller konstigt issue blir null, så att resten av listan klarar sig.
function tolka(nod: IssueNod | null | undefined): { issue: Issue; svar: string | null } | null {
  try {
    if (!nod) return null;
    const svar = nod.comments.nodes.map((c) => c.body.trim()).filter((b) => b.startsWith("Svar:"));
    return {
      issue: { nummer: nod.number, rubrik: nod.title, oppen: nod.state === "OPEN", etiketter: nod.labels.nodes.map((l) => l.name) },
      svar: svar.length ? svar[svar.length - 1].slice("Svar:".length).trim() : null,
    };
  } catch {
    return null;
  }
}

export function skapaGitHub(token: string, repo: string, f: typeof fetch = (...a) => fetch(...a)): GitHub {
  const [agare, namn] = repo.split("/");
  async function anrop(url: string, init: RequestInit = {}): Promise<unknown> {
    const huvuden: Record<string, string> = {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "bok-forslag",
      "X-GitHub-Api-Version": "2022-11-28",
    };
    if (init.body) huvuden["Content-Type"] = "application/json";
    const res = await f(url, { ...init, headers: huvuden });
    if (!res.ok) throw new GitHubFel(res.status);
    return res.json();
  }
  return {
    async skapaIssue(rubrik, text, etiketter) {
      const j = (await anrop(`https://api.github.com/repos/${repo}/issues`, {
        method: "POST",
        body: JSON.stringify({ title: rubrik, body: text, labels: etiketter }),
      })) as { number: number };
      return j.number;
    },
    async hamtaManga(nummer) {
      const ut = new Map<number, { issue: Issue; svar: string | null } | null>();
      if (nummer.length === 0) return ut;
      if (!nummer.every((n) => Number.isInteger(n) && n > 0)) throw new GitHubFel("ogiltigt nummer");
      const falt = nummer
        .map((n) => `i${n}: issue(number: ${n}) { number title state labels(first: 30) { nodes { name } } comments(last: 30) { nodes { body } } }`)
        .join(" ");
      const query = `query { repository(owner: ${JSON.stringify(agare)}, name: ${JSON.stringify(namn)}) { ${falt} } }`;
      const j = (await anrop("https://api.github.com/graphql", { method: "POST", body: JSON.stringify({ query }) })) as {
        data?: { repository?: Record<string, IssueNod | null> | null } | null;
      };
      const repository = j?.data?.repository;
      if (!repository) throw new GitHubFel("utan data");
      for (const n of nummer) {
        ut.set(n, tolka(repository[`i${n}`]));
      }
      return ut;
    },
  };
}
