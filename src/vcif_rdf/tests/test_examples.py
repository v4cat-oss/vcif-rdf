"""End-to-end tests for the two canonical example fixtures."""
from __future__ import annotations

from vcif_rdf import validate, cells
from rdflib import URIRef


def test_agda_import_carrier_conforms(agda_import_graph):
    validate(agda_import_graph)


def test_hf_dbe_closure_carrier_conforms(hf_dbe_closure_graph):
    validate(hf_dbe_closure_graph)


def test_hf_dbe_closure_kquery_matches_expectation(hf_dbe_closure_graph):
    """The HF-DBE closure cover should classify CLAIM-DBE-produces-shadows
    into cell 11 (in both observers) — the closure invariant."""
    cover = URIRef('https://example.org/hf-dbe#cover')
    in_set = URIRef('https://example.org/hf-dbe#inSet')
    result = cells(hf_dbe_closure_graph, cover, in_set)
    claim = URIRef('https://example.org/hf-dbe#claimDbeShadows')
    assert claim in result['11']
    assert all(result[c] == [] for c in ('00', '01', '10'))
