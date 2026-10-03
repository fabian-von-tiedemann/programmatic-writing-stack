import { describe, expect, it } from "vitest";
import { skapaGitHub } from "../src/github";

function fejkFetch(svar: Record<string, unknown>, status = 200) {
  const anrop: { url: string; init: RequestInit }[] = [];
  const f = (async (url: string, init: RequestInit = {}) => {
    anrop.push({ url, init });
    const nyckel = Object.keys(svar).find((k) => url.endsWith(k));
    return new Response(JSON.stringify(nyckel ? svar[nyckel] : {}), { status });
  }) as unknown as typeof fetch;
  return { f, anrop };
}

describe("skapaGitHub", () => {
  it("skapar issue med rätt huvuden och etiketter", async () => {
    const { f, anrop } = fejkFetch({ "/issues": { number: 7 } });
    const gh = skapaGitHub("hemlig", "fabian-von-tiedemann/bok-forslag", f);
    expect(await gh.skapaIssue("Rubrik", "Text", ["forslag"])).toBe(7);
    const { url, init } = anrop[0];
    expect(url).toBe("https://api.github.com/repos/fabian-von-tiedemann/bok-forslag/issues");
    expect(init.method).toBe("POST");
    const huvuden = new Headers(init.headers);
    expect(huvuden.get("Authorization")).toBe("Bearer hemlig");
    expect(huvuden.get("User-Agent")).toBe("bok-forslag");
    expect(JSON.parse(init.body as string)).toEqual({ title: "Rubrik", body: "Text", labels: ["forslag"] });
  });

  it("läser issue och senaste Svar:-kommentaren", async () => {
    const { f } = fejkFetch({
      "/issues/7": { number: 7, title: "R", state: "closed", labels: [{ name: "infort:2.1.0" }, "status:planerad"] },
      "/issues/7/comments?per_page=100": [{ body: "Intern anteckning" }, { body: "Svar: Först" }, { body: "  Svar:  Sist " }],
    });
    const gh = skapaGitHub("t", "o/r", f);
    expect(await gh.hamtaIssue(7)).toEqual({ nummer: 7, rubrik: "R", oppen: false, etiketter: ["infort:2.1.0", "status:planerad"] });
    expect(await gh.hamtaSvar(7)).toBe("Sist");
  });

  it("utan svar och vid fel", async () => {
    const { f } = fejkFetch({ "/issues/8/comments?per_page=100": [{ body: "Bara internt" }] });
    expect(await skapaGitHub("t", "o/r", f).hamtaSvar(8)).toBeNull();
    const fel = fejkFetch({}, 500);
    await expect(skapaGitHub("t", "o/r", fel.f).skapaIssue("a", "b", [])).rejects.toThrow("GitHub 500");
  });
});
