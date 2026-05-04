"""
vcif_rdf.validator — pyshacl-driven layered validation.

Layer 1: SHACL Core well-formedness against carrier-form.ttl.
Layer 2: SHACL-SPARQL self-hosting closure against
         carrier-self-hosting.ttl.

A graph is *carrier-conformant* iff both layers pass.
"""
from __future__ import annotations

from rdflib import Graph
import pyshacl

from .ontology_loader import shapes_graph, carrier_graph


class CarrierShapeError(ValueError):
    """SHACL validation failure. Carries the conforms flag, results graph,
    and human-readable text."""

    def __init__(self, results_text: str, results_graph: Graph):
        super().__init__(results_text)
        self.results_text = results_text
        self.results_graph = results_graph


def validate_carrier(data: Graph, *, inference: str = 'rdfs') -> None:
    """Run both SHACL passes against the data graph. Raise on failure.

    The data graph is *augmented* with the carrier ontology before
    validation so sh:class checks against vc:NodeAssertion / vc:EdgeAssertion
    resolve. The original data graph is not mutated.
    """
    augmented = Graph()
    augmented += data
    augmented += carrier_graph()

    conforms, results_graph, results_text = pyshacl.validate(
        augmented,
        shacl_graph=shapes_graph(),
        inference=inference,
        advanced=True,           # enables SHACL-SPARQL constraints
        meta_shacl=False,
        debug=False,
    )
    if not conforms:
        raise CarrierShapeError(results_text, results_graph)
