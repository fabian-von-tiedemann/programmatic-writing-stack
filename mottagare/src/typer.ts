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

export type Status = "mottaget" | "planerat" | "infort" | "avbojt";

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
  spara(rad: Rad): Promise<void>;
  lista(nyckelHash: string, max: number): Promise<Omit<Rad, "nyckelHash">[]>;
}

export interface Issue {
  nummer: number;
  rubrik: string;
  oppen: boolean;
  etiketter: string[];
}

export interface GitHub {
  skapaIssue(rubrik: string, text: string, etiketter: string[]): Promise<number>;
  hamtaIssue(nummer: number): Promise<Issue>;
  hamtaSvar(nummer: number): Promise<string | null>;
}

export interface Beroenden {
  lagring: Lagring;
  github: GitHub;
  begransa(nyckelHash: string, ip: string): Promise<boolean>;
  nu(): Date;
  nyttId(): string;
}
