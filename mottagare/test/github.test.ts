import { describe, expect, it } from "vitest";
import { diagnos, GitHubFel, skapaGitHub } from "../src/github";

function fejkFetch(svar: Record<string, unknown>, status = 200) {
  const anrop: { url: string; init: RequestInit }[] = [];
  const f = (async (url: string, init: RequestInit = {}) => {
    anrop.push({ url, init });
    const nyckel = Object.keys(svar).find((k) => url.endsWith(k));
    return new Response(JSON.stringify(nyckel ? svar[nyckel] : {}), { status });
  }) as unknown as typeof fetch;
  return { f, anrop };
}

const issueNod = (number: number, over: Record<string, unknown> = {}) => ({
  number,
  title: `R${number}`,
  state: "OPEN",
  labels: { nodes: [{ name: "forslag" }] },
  comments: { nodes: [] },
  ...over,
});

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

  it("hämtar alla issues med ett enda GraphQL-anrop", async () => {
    const { f, anrop } = fejkFetch({
      "/graphql": {
        data: {
          repository: {
            i7: issueNod(7, {
              state: "CLOSED",
              labels: { nodes: [{ name: "infort:2.1.0" }, { name: "status:planerad" }] },
              comments: { nodes: [{ body: "Intern anteckning" }, { body: "Svar: Först" }, { body: "  Svar:  Sist " }, { body: "Intern igen" }] },
            }),
            i8: issueNod(8, { comments: { nodes: [{ body: "Bara internt" }] } }),
            i9: null,
          },
        },
        errors: [{ type: "NOT_FOUND", path: ["repository", "i9"] }],
      },
    });
    const gh = skapaGitHub("hemlig", "fabian-von-tiedemann/bok-forslag", f);
    const ut = await gh.hamtaManga([7, 8, 9]);
    expect(anrop).toHaveLength(1);
    const { url, init } = anrop[0];
    expect(url).toBe("https://api.github.com/graphql");
    expect(init.method).toBe("POST");
    expect(new Headers(init.headers).get("Authorization")).toBe("Bearer hemlig");
    const fraga = (JSON.parse(init.body as string) as { query: string }).query;
    expect(fraga).toContain('repository(owner: "fabian-von-tiedemann", name: "bok-forslag")');
    for (const n of [7, 8, 9]) expect(fraga).toContain(`i${n}: issue(number: ${n})`);
    expect(ut.get(7)).toEqual({ issue: { nummer: 7, rubrik: "R7", oppen: false, etiketter: ["infort:2.1.0", "status:planerad"] }, svar: "Sist" });
    expect(ut.get(8)).toEqual({ issue: { nummer: 8, rubrik: "R8", oppen: true, etiketter: ["forslag"] }, svar: null });
    expect(ut.get(9)).toBeNull();
  });

  it("inga nummer ger inget anrop", async () => {
    const { f, anrop } = fejkFetch({});
    expect((await skapaGitHub("t", "o/r", f).hamtaManga([])).size).toBe(0);
    expect(anrop).toHaveLength(0);
  });

  it("vägrar nummer som inte är heltal", async () => {
    const { f, anrop } = fejkFetch({});
    await expect(skapaGitHub("t", "o/r", f).hamtaManga([1.5])).rejects.toThrow();
    await expect(skapaGitHub("t", "o/r", f).hamtaManga([Number.NaN])).rejects.toThrow();
    expect(anrop).toHaveLength(0);
  });

  it("HTTP-fel eller svar utan data kastar", async () => {
    const fel = fejkFetch({}, 500);
    await expect(skapaGitHub("t", "o/r", fel.f).skapaIssue("a", "b", [])).rejects.toThrow("GitHub 500");
    await expect(skapaGitHub("t", "o/r", fel.f).hamtaManga([1])).rejects.toThrow("GitHub 500");
    const utanData = fejkFetch({ "/graphql": { errors: [{ message: "Bad" }] } });
    await expect(skapaGitHub("t", "o/r", utanData.f).hamtaManga([1])).rejects.toBeInstanceOf(GitHubFel);
    const utanRepo = fejkFetch({ "/graphql": { data: { repository: null } } });
    await expect(skapaGitHub("t", "o/r", utanRepo.f).hamtaManga([1])).rejects.toBeInstanceOf(GitHubFel);
  });
});

describe("diagnos", () => {
  it("visar bara felets namn, och statuskoden för GitHub-fel", () => {
    expect(diagnos(new GitHubFel(401))).toBe("GitHub 401");
    expect(diagnos(new TypeError("hemlig text ur förslaget"))).toBe("TypeError");
    expect(diagnos(new Error("Bearer abc"))).toBe("Error");
    expect(diagnos("en sträng")).toBe("okänt fel");
  });
});
