# vcif-rdf — RDF/SHACL/SPARQL carrier for v4cat

> **Version**: 0.1
> **Status**: Alpha
> **Substrate-column counterpart to**: [vcif][vcif] (JSON Schema)
> **Algebraic basis**: [v4cat `theory.md` § 15][theory15]

[vcif]: https://github.com/v4cat-oss/vcif
[v4cat]: https://github.com/v4cat-oss/v4cat
[theory15]: https://github.com/v4cat-oss/v4cat/blob/main/src/v4cat/theory.md

vcif-rdf is the RDF/SHACL/SPARQL substrate of the (depth × substrate)
carrier grid for v4cat. Same v4cat semantics as vcif; same six profiles;
different syntactic substrate, validator, and query language.

## Slogan

> **RISC writes are translations; kquery is the V₄ coordinate chart.**

(From v4cat `theory.md` § 15.16.) The RDF carrier is one named
projection of the assertion-history group action `H = ℤ^𝔄`; a Turtle
file carries `vc:NodeAssertion` and `vc:EdgeAssertion` records that
project (depending on profile) one of `h ∈ H`, `π(h)`, `χ_{A,B}(π(h))`,
or further-quotients thereof.

## 1. The decisive distinction: carrier predicates vs object-language nodes

The RDF carrier draws a strict layering:

| Layer | Examples | Where they live |
|---|---|---|
| **Carrier predicates** (fixed) | `vc:source`, `vc:edgeKind`, `vc:target`, `vc:cover`, `vc:cell`, `vc:member`, `vc:identifier`, `vc:label` | RDF predicates declared in `carrier.ttl` |
| **v4cat object-language nodes** | `has-kind`, `references-def`, `kind:Def`, `HF-DBE`, ... | Ordinary `vc:NodeAssertion`s, named via `vc:identifier` |

So the wrong way is:

```turtle
:term1 :has-kind :kindDef .       # has-kind as RDF predicate — WRONG
```

The right way is:

```turtle
:hasKind a vc:NodeAssertion ;
  vc:identifier "has-kind" .

:e1 a vc:EdgeAssertion ;
  vc:source :term1 ;
  vc:edgeKind :hasKind ;
  vc:target :kindDef .
```

`vc:source`, `vc:edgeKind`, and `vc:target` are *carrier slots* — fixed
RDF predicates whose only job is to encode v4cat assertion records.
`:hasKind` is an ordinary v4cat node that occupies the edge-kind slot
of three (or more) edge assertions. Whether `:hasKind` is "property-
like" is a *query result* over shared occupancy of `vc:edgeKind`, not a
primitive declaration. Per v4cat discipline (`shadow_kquery_orbit.md`,
`theory.md` § 15.10): there are no first-class properties.

## 2. Two-layer enforcement

```text
Turtle document
  → Layer 1: SHACL Core               (shapes/carrier-form.ttl)
  → Layer 2: SHACL-SPARQL             (shapes/carrier-self-hosting.ttl)
  → SPARQL kquery                     (queries/kquery.rq)
  → import via SymmetryCatalogue API  (vcif_rdf.importer)
```

**Layer 1** (SHACL Core) validates that every `vc:EdgeAssertion` has
exactly one `vc:source`, one `vc:edgeKind`, and one `vc:target`, each
pointing at a `vc:NodeAssertion`. Every `vc:NodeAssertion` has exactly
one `vc:identifier`. Every `vc:CoverAssertion` has exactly one
`vc:universe`, `vc:leftObserver`, and `vc:rightObserver`. Carrier
well-formedness, no semantic claims.

**Layer 2** (SHACL-SPARQL) validates the **carrier-self-hosting
closure**: every carrier slot (`vc:source`, `vc:edgeKind`, `vc:target`,
...) and every carrier class (`vc:NodeAssertion`, `vc:EdgeAssertion`,
...) is itself a `vc:NodeAssertion` with a stable identifier. This
closes the loophole that would otherwise let the RDF carrier hide its
own representational machinery from v4cat. Both passes run
automatically when `vcif_rdf.validate(graph)` is called.

## 3. Carrier ontology (carrier.ttl)

Declared classes (carrier roles) and their semantic content:

| Carrier class | Group-theoretic content |
|---|---|
| `vc:NodeAssertion` | `Nₓ ∈ 𝔄_node` — a node-assertion atom |
| `vc:EdgeAssertion` | `Eₛ,ₖ,ₜ ∈ 𝔄_edge` — an edge-assertion atom |
| `vc:CoverAssertion` | `(U, A, B)` — a kquery frame |
| `vc:CellAssertion` | `(u, χ_{A,B}(u))` — one materialized point of the V₄ chart |
| `vc:ProjectionAssertion` | a named quotient over a cover |
| `vc:TensionAssertion` | a declarative recognizer (parameters + cover + cell actions) |
| `vc:DerivationAssertion` | the audit record of one cell-action application |
| `vc:ResidueAssertion` | a non-empty cell that the recognizer chose not to derive into |
| `vc:ExpectationAssertion` | a closure check — per-cell `{empty, nonempty, min/max}` |

The cell labels are `vc:cell00`, `vc:cell01`, `vc:cell10`, `vc:cell11`
— each declared as a `vc:NodeAssertion` so it can be referenced as a
member of any V₄ classification.

## 4. SPARQL kquery (queries/kquery.rq)

The parametric SPARQL `SELECT` returns `(?u, ?cell)` rows — one per
member of the cover's universe, classified into one of the four V₄
cells:

```sparql
SELECT ?u ?cell
WHERE {
  $cover vc:universe ?universe ;
         vc:leftObserver ?left ;
         vc:rightObserver ?right .

  ?uMembership a vc:EdgeAssertion ;
               vc:source ?u ;
               vc:edgeKind $inSetKind ;
               vc:target ?universe .

  BIND(EXISTS { ... vc:target ?left  } AS ?inA)
  BIND(EXISTS { ... vc:target ?right } AS ?inB)

  BIND(IF(?inA && ?inB, vc:cell11,
       IF(?inA && !?inB, vc:cell10,
       IF(!?inA && ?inB, vc:cell01, vc:cell00))) AS ?cell)
}
```

The `vcif_rdf.kquery.cells(graph, cover, in_set)` Python helper
groups the rows by cell and returns `{'00': [...], '01': [...], '10':
[...], '11': [...]}`.

## 5. Profiles

Same six profiles as vcif. Each is a `vc:NodeAssertion` of identifier
`profile:v4cat.<name>` shipped in `ontology/profiles/<name>.ttl`.

| Profile | Projection-depth | Operative |
|---|---|---|
| `v4cat.snapshot` | `π(h)` (visible-state quotient) | full snapshot |
| `v4cat.patch` | `h ∈ H` (operation-log; group-faithful) | additive translations |
| `v4cat.vocabulary` | (signature, not state) | declares basis 𝔄 |
| `v4cat.recognizer-package` | (operator, not state) | tensions + cell actions |
| `v4cat.closure-report` | `χ_{A,B}(π(h))` (V₄-cover) | covers + cells + expectations |
| `v4cat.residue-report` | further-quotient | residues from prior closures |

The four state-carrying profiles (snapshot, patch, closure-report,
residue-report) lie on the projection-depth axis with patch as the
group-faithful root. The two operator/signature profiles (vocabulary,
recognizer-package) sit on a parallel axis declaring basis and
recognizer-action layer.

## 6. Self-hosting

The carrier ontology mirrors its own machinery as `vc:NodeAssertion`s:

- Every `vc:CarrierClass` (`vc:NodeAssertion`, `vc:EdgeAssertion`, ...)
  is also itself a `vc:NodeAssertion` with identifier
  `carrier-class:<Name>`.
- Every carrier slot (`vc:source`, `vc:edgeKind`, `vc:target`, ...) is
  also itself a `vc:NodeAssertion` with identifier
  `carrier-slot:<name>`.

This satisfies the SHACL-SPARQL closure check at Layer 2. The
catalogue can therefore reason about the carrier *as a v4cat object*,
which is the recursive bootstrap that makes vcif-rdf a *self-hosted*
RDF carrier rather than just an RDF schema for v4cat data.

## 7. Importer

`vcif_rdf.importer.apply(graph, catalogue)` walks the graph's
`vc:NodeAssertion` and `vc:EdgeAssertion` subjects and dispatches to
v4cat's public ISA verbs (`introduce_node`, `edge`). It is a *boring
loop* — exactly what `theory.md` § 15 implies: the import is a
composition of left-translations in `H`. The importer is idempotent
(re-importing produces the same end-state) via
`sqlite3.IntegrityError` suppression on the v4cat side.

The importer never uses an RDF predicate as a v4cat edge kind. Per the
carrier-vs-object discipline, all object-language information flows
through `vc:source` / `vc:edgeKind` / `vc:target` triples on
`vc:EdgeAssertion` records.

## 8. CLI

```sh
vcif-rdf validate doc.ttl
vcif-rdf inspect doc.ttl
vcif-rdf dry-run --catalogue cat.db doc.ttl
vcif-rdf import --catalogue cat.db doc.ttl
```

`validate` runs both SHACL passes. `inspect` prints carrier-class
counts. `dry-run` validates and reports proposed mutations. `import`
applies via v4cat's public ISA.

## 9. Negative space

By design, vcif-rdf never:

- introduces RDF predicates beyond the fixed carrier slots,
- treats any object-language item as `rdf:Property`,
- uses `rdfs:subClassOf` / `rdf:type` to encode v4cat kinds (kinds are
  carried via `vc:edgeKind ex:hasKind` triples on `vc:EdgeAssertion`
  records),
- embeds raw SQL or executable code,
- relies on `vc:` predicates outside the eight slots declared in
  `carrier.ttl`.

If a graph violates any of these, it is not a valid vcif-rdf carrier;
the SHACL validator rejects it (or the importer refuses to dispatch).

## 10. Relationship to vcif and vcif-hlo

vcif, vcif-rdf, and [vcif-hlo][vcif-hlo] are **substrate-column
siblings** in the (depth × substrate) carrier grid registered in
v4cat's cotype:

[vcif-hlo]: https://github.com/v4cat-oss/vcif-hlo

| Depth | JSON (vcif) | RDF (vcif-rdf) | Tensor (vcif-hlo) |
| --- | --- | --- | --- |
| operation-log | `v4cat.patch` | `v4cat.patch` | `IdDictionary` + ordered ops |
| state-snapshot | `v4cat.snapshot` | `v4cat.snapshot` | `ReferentUniverseTensor` |
| V₄-cover | `v4cat.closure-report` | `v4cat.closure-report` | `CoverTensor` (cell ∈ {00,01,10,11}) |
| residue | `v4cat.residue-report` | `v4cat.residue-report` | cell-mask projection |

No column is canonical. The catalogue's identity is unchanged across
substrates. A round-trip that reads from one column and writes to
another through v4cat's public API produces identical catalogue
state — the **cross-substrate parity** invariant. vcif-hlo
operationalises kquery as `cell_code = 2·A_live + B_live` (per
[v4cat `theory.md` § 15][theory15]), which makes the V₄-cover row
particularly efficient in the tensor substrate.
