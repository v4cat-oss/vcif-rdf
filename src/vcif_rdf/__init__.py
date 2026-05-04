"""
vcif_rdf — RDF/SHACL/SPARQL carrier for v4cat catalogues.

Public API:

    parse(text_or_path)             load Turtle into an rdflib.Graph
    validate(graph)                 SHACL Core + SHACL-SPARQL
    apply(graph, catalogue)         mutate via v4cat public ISA
    cells(graph, cover, in_set)     SPARQL kquery → V₄ partition

The catalogue's identity is unchanged by vcif-rdf — all writes go
through `v4cat.SymmetryCatalogue`'s public verbs (introduce_node,
edge). vcif-rdf's job is to validate and dispatch over RDF;
v4cat is the substrate.

Algebraic basis: v4cat theory.md § 15. RISC writes are translations;
kquery is the V₄ coordinate chart.
"""
from rdflib import Graph

from .validator import validate_carrier as validate, CarrierShapeError
from .importer import apply
from .kquery import cells


def parse(text_or_path: str) -> Graph:
    """Parse a Turtle string or read a file path into an rdflib.Graph."""
    g = Graph()
    if isinstance(text_or_path, str) and (
        text_or_path.endswith('.ttl') or text_or_path.endswith('.n3')
    ):
        g.parse(text_or_path, format='turtle')
    else:
        g.parse(data=text_or_path, format='turtle')
    return g


__all__ = [
    'parse',
    'validate',
    'apply',
    'cells',
    'CarrierShapeError',
]
