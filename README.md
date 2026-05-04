# vcif-rdf — RDF/SHACL/SPARQL carrier for v4cat catalogues

The **substrate-column counterpart to [vcif][vcif]**. Same v4cat
semantics; same six profiles; different syntactic substrate (RDF/Turtle
instead of JSON), different validator (SHACL instead of JSON Schema),
different query language (SPARQL instead of Python set_expr eval).

[vcif]: https://github.com/v4cat-oss/vcif
[v4cat]: https://github.com/v4cat-oss/v4cat

## Algebraic basis

Per [v4cat `theory.md` § 15][theory15]: v4cat is a free-abelian
assertion-history group action `H = ℤ^𝔄`; the visible catalogue is the
support quotient `π(H)`; `kquery` is the V₄-equivariant coordinate
chart of the observer-pair group `V₄^U`. **RISC writes are
translations; kquery is the V₄ coordinate chart.**

vcif-rdf carries v4cat assertions as `vc:NodeAssertion` and
`vc:EdgeAssertion` records; it never uses RDF predicates as v4cat
edge kinds.

[theory15]: https://github.com/v4cat-oss/v4cat/blob/main/src/v4cat/theory.md

## Core principle

The carrier draws a strict distinction:

| Layer | What lives here |
|---|---|
| **Carrier predicates** (fixed RDF properties) | `vc:source`, `vc:edgeKind`, `vc:target`, `vc:cover`, `vc:cell`, `vc:member`, `vc:identifier`, `vc:label` |
| **v4cat object-language nodes** (ordinary `vc:NodeAssertion`s) | `has-kind`, `references-def`, `kind:Def`, `HF-DBE`, `CLAIM-DBE-produces-shadows`, ... |

So instead of:

```turtle
:term1 :has-kind :kindDef .          # WRONG — has-kind as RDF predicate
```

we write:

```turtle
:e1 a vc:EdgeAssertion ;
    vc:source :term1 ;
    vc:edgeKind :hasKind ;
    vc:target :kindDef .             # has-kind is a node, not a predicate
```

This preserves v4cat's discipline: there are no first-class properties.

## Two-layer enforcement

```text
RDF document
  → Layer 1: SHACL Core      (carrier well-formedness)
  → Layer 2: SHACL-SPARQL    (carrier-slot self-hosting closure)
  → SPARQL kquery            (V₄-cell classification)
  → import via SymmetryCatalogue API   (vcif_rdf.importer)
```

Layer 1 validates that every `vc:EdgeAssertion` has exactly one
`vc:source`, one `vc:edgeKind`, and one `vc:target`. Layer 2 validates
that the carrier slots themselves are hosted as `vc:NodeAssertion`s
with `has-kind → kind:CarrierSlot` edges.

## Profiles

Same six profiles as vcif:

| Profile | Group-theoretic content |
|---|---|
| `v4cat.snapshot` | `π(h)` — full visible-state |
| `v4cat.patch` | `h ∈ H` — operation-log carrier |
| `v4cat.vocabulary` | declares the basis `𝔄` |
| `v4cat.recognizer-package` | tensions + cell actions |
| `v4cat.closure-report` | `χ_{A,B}(π(h))` — V₄-cover |
| `v4cat.residue-report` | further-quotient of cells |

Each profile has its own `.ttl` ontology in `src/vcif_rdf/ontology/profiles/`.

## Install

```sh
pip install vcif-rdf       # pulls v4cat, rdflib, pyshacl
```

## CLI

```sh
vcif-rdf validate doc.ttl                              # SHACL Core + SHACL-SPARQL
vcif-rdf inspect doc.ttl                               # parse + print structure
vcif-rdf dry-run --catalogue cat.db doc.ttl
vcif-rdf import --catalogue cat.db doc.ttl
```

## Layout

```text
vcif-rdf/
├── pyproject.toml
├── LICENSE                            MIT (Python tooling)
├── README.md                          this file
├── docs/
│   ├── spec.md                        full RDF carrier spec
│   └── examples/
│       ├── agda-import.ttl
│       └── hf-dbe-closure.ttl
└── src/vcif_rdf/
    ├── __init__.py
    ├── __main__.py                    enables `python -m vcif_rdf`
    ├── cli.py                         console-script entry
    ├── ontology/
    │   ├── LICENSE                    Apache-2.0 (RDF schemas)
    │   ├── carrier.ttl                vc: vocabulary
    │   └── profiles/
    │       ├── snapshot.ttl
    │       ├── patch.ttl
    │       ├── vocabulary.ttl
    │       ├── recognizer-package.ttl
    │       ├── closure-report.ttl
    │       └── residue-report.ttl
    ├── shapes/
    │   ├── carrier-form.ttl           SHACL Core well-formedness
    │   └── carrier-self-hosting.ttl   SHACL-SPARQL closure
    ├── queries/
    │   ├── kquery.rq                  parametric V₄-cell classification
    │   ├── projections/
    │   └── recognizers/
    ├── ontology_loader.py             importlib.resources access
    ├── validator.py                   pyshacl-driven validation
    ├── importer.py                    apply mode (uses v4cat public ISA)
    ├── kquery.py                      SPARQL-driven V₄ evaluator
    ├── recognizers.py                 SPARQL recognizer dispatcher
    └── tests/
        └── ...
```

## Relationship to v4cat-oss siblings

| Distribution | Substrate | Validator | Query language |
|---|---|---|---|
| [v4cat-oss/v4cat][v4cat] | Python + SQLite | (none — implementation) | Python `kquery` |
| [v4cat-oss/v4cat-mcp](https://github.com/v4cat-oss/v4cat-mcp) | MCP-over-stdio (RPC) | (transport) | MCP tool args |
| [v4cat-oss/vcif][vcif] | JSON | JSON Schema 2020-12 | Python set_expr eval |
| [v4cat-oss/vcif-rdf](https://github.com/v4cat-oss/vcif-rdf) (this repo) | RDF/Turtle | SHACL + SHACL-SPARQL | SPARQL 1.1 |

The catalogue's identity is unchanged across all four. vcif and
vcif-rdf are *substrate-column siblings* in the (depth × substrate)
carrier grid registered in v4cat's cotype.

## License

Python tooling: MIT. RDF schemas in `src/vcif_rdf/ontology/`:
Apache-2.0 (so non-Python tools can reimplement freely).
