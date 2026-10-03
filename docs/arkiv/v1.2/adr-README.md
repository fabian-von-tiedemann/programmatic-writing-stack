# ADR — Architecture Decision Records

Varje större arkitektur-beslut i bokprojektet får en numrerad ADR. Format inspirerat av Michael Nygard's klassiska ADR-template.

## Filnamn

`NNNN-<kort-titel>.md` (zero-padded fyra siffror)

## Innehåll per ADR

```markdown
# ADR NNNN — <titel>

**Status:** [Proposed | Accepted | Deprecated | Superseded by ADR NNNN]
**Datum:** YYYY-MM-DD

## Kontext

Vad var problemet? Vad utlöste behovet av ett beslut?

## Beslut

Vad bestämde vi? En mening + utveckling.

## Konsekvenser

### Positiva

- ...

### Negativa

- ...

### Neutrala

- ...

## Alternativ som övervägdes

- **Alternativ A:** ... — avfärdat eftersom ...
- **Alternativ B:** ... — avfärdat eftersom ...

## Referenser

- (länkar till diskussioner, relaterade ADR:er, externa källor)
```

## Exempel på ADR-frågor

- Layered markup-pipeline (per kapitel) ja eller nej?
- Story-graph query-lager — eget script eller Notion?
- Audiobook-pipeline — Eleven Labs eller Murf?
- Hur stor del av canon ska vara JSON vs MD?

## Disciplin

1. Inget större tekniskt beslut utan ADR.
2. ADR:er är immutable — om beslutet ändras, skriv ny ADR med "Supersedes ADR XYZ".
3. ADR:er är *kort* — max 2 sidor. Längre = kanske fel scope.
