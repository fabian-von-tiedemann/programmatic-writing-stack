export const TYPER = ["forbattring", "problem", "fraga", "lardom"] as const;
export type Typ = (typeof TYPER)[number];

export interface Forslag {
  typ: Typ;
  text: string;
  sammanhang: string;
  version: string;
  lage: string;
  roll: string;
}

// "okand": issuet gick inte att läsa (till exempel borttaget).
export type Status = "mottaget" | "planerat" | "infort" | "avbojt" | "okand";

export interface ForslagStatus {
  id: string;
  issue: number;
  rubrik: string;
  skapad: string;
  status: Status;
  version: string | null;
  svar: string | null;
}

export interface Rad {
  id: string;
  nyckelHash: string;
  issue: number;
  skapad: string;
}

export interface Lagring {
  arSparrad(nyckelHash: string): Promise<boolean>;
  antalSedan(nyckelHash: string, sedan: string): Promise<number>;
  antalTotaltSedan(sedan: string): Promise<number>;
  spara(rad: Rad): Promise<void>;
  lista(nyckelHash: string, max: number): Promise<Omit<Rad, "nyckelHash">[]>;
  antalIpIdag(ipHash: string, dag: string): Promise<number>;
  raknaIp(ipHash: string, dag: string): Promise<void>;
}

export interface Issue {
  nummer: number;
  rubrik: string;
  oppen: boolean;
  etiketter: string[];
}

export interface GitHub {
  skapaIssue(rubrik: string, text: string, etiketter: string[]): Promise<number>;
  // Ett enda anrop för alla nummer; null för issues som saknas.
  hamtaManga(nummer: number[]): Promise<Map<number, { issue: Issue; svar: string | null } | null>>;
}

export interface Beroenden {
  lagring: Lagring;
  github: GitHub;
  begransa(nyckelHash: string, ip: string): Promise<boolean>;
  begransaLasning(nyckelHash: string, ip: string): Promise<boolean>;
  // ip är redan avkortad (ipNyckel); dag är UTC-datumet "ÅÅÅÅ-MM-DD".
  ipHash(ip: string, dag: string): Promise<string>;
  nu(): Date;
  nyttId(): string;
}
