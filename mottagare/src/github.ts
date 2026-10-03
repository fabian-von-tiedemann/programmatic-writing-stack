import type { GitHub, Issue } from "./typer";

export function skapaGitHub(token: string, repo: string, f: typeof fetch = (...a) => fetch(...a)): GitHub {
  const bas = `https://api.github.com/repos/${repo}`;
  async function anrop(vag: string, init: RequestInit = {}): Promise<unknown> {
    const huvuden: Record<string, string> = {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "bok-forslag",
      "X-GitHub-Api-Version": "2022-11-28",
    };
    if (init.body) huvuden["Content-Type"] = "application/json";
    const res = await f(`${bas}${vag}`, { ...init, headers: huvuden });
    if (!res.ok) throw new Error(`GitHub ${res.status}`);
    return res.json();
  }
  return {
    async skapaIssue(rubrik, text, etiketter) {
      const j = (await anrop("/issues", { method: "POST", body: JSON.stringify({ title: rubrik, body: text, labels: etiketter }) })) as { number: number };
      return j.number;
    },
    async hamtaIssue(nummer): Promise<Issue> {
      const j = (await anrop(`/issues/${nummer}`)) as { number: number; title: string; state: string; labels: (string | { name: string })[] };
      return { nummer: j.number, rubrik: j.title, oppen: j.state === "open", etiketter: j.labels.map((l) => (typeof l === "string" ? l : l.name)) };
    },
    async hamtaSvar(nummer) {
      const j = (await anrop(`/issues/${nummer}/comments?per_page=100`)) as { body: string }[];
      const svar = j.map((c) => c.body.trimStart()).filter((b) => b.startsWith("Svar:"));
      return svar.length ? svar[svar.length - 1].slice("Svar:".length).trim() : null;
    },
  };
}
