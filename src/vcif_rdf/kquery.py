"""
vcif_rdf.kquery — SPARQL-driven V₄ cell evaluator.

For a given CoverAssertion in an rdflib graph, run the parametric
kquery.rq SELECT to classify every member of the cover's universe
into one of the four V₄ cells. Returns the four-cell partition.

Per theory.md § 15.5: kquery is the V₄-equivariant coordinate chart
of the observer-pair group action; this module is the SPARQL
realisation of that chart on RDF data.
"""
from __future__ import annotations

from rdflib import Graph, URIRef

from .ontology_loader import kquery_template

# vc:cell00 / vc:cell01 / vc:cell10 / vc:cell11 IRIs as plain strings
# for keying the result dict.
_CARRIER = 'https://v4cat-oss.github.io/vcif-rdf/carrier#'
_CELL_NAMES = {
    URIRef(_CARRIER + 'cell00'): '00',
    URIRef(_CARRIER + 'cell01'): '01',
    URIRef(_CARRIER + 'cell10'): '10',
    URIRef(_CARRIER + 'cell11'): '11',
}


def cells(
    data: Graph,
    cover: URIRef,
    in_set_kind: URIRef,
) -> dict[str, list[URIRef]]:
    """Classify each member of `cover`'s universe by the V₄ chart.

    `in_set_kind` is the NodeAssertion that membership-edges use as
    their `vc:edgeKind` — typically `ex:inSet` per the writeup §11.

    Returns a dict with keys '00', '01', '10', '11', each a list of
    URIRefs (the members of that cell).
    """
    result = {'00': [], '01': [], '10': [], '11': []}
    rows = data.query(
        kquery_template(),
        initBindings={'cover': cover, 'inSetKind': in_set_kind},
    )
    for u, cell in rows:
        cell_label = _CELL_NAMES.get(cell)
        if cell_label is None:
            continue
        result[cell_label].append(u)
    return result
