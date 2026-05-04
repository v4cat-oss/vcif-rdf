"""Validator tests — SHACL Core well-formedness."""
from __future__ import annotations

import pytest
from rdflib import Graph

from vcif_rdf import validate, CarrierShapeError


def test_minimal_snapshot_passes(minimal_snapshot):
    validate(minimal_snapshot)


def test_agda_import_passes(agda_import_graph):
    validate(agda_import_graph)


def test_hf_dbe_closure_passes(hf_dbe_closure_graph):
    validate(hf_dbe_closure_graph)


def test_edge_missing_source_fails():
    g = Graph()
    g.parse(data="""
@prefix vc: <https://v4cat-oss.github.io/vcif-rdf/carrier#> .
@prefix ex: <https://example.org/bad#> .

ex:nA a vc:NodeAssertion ; vc:identifier "a" .
ex:hasKind a vc:NodeAssertion ; vc:identifier "has-kind" .

ex:e1 a vc:EdgeAssertion ;
  vc:edgeKind ex:hasKind ;
  vc:target ex:nA .
""", format='turtle')
    with pytest.raises(CarrierShapeError):
        validate(g)


def test_edge_missing_kind_fails():
    g = Graph()
    g.parse(data="""
@prefix vc: <https://v4cat-oss.github.io/vcif-rdf/carrier#> .
@prefix ex: <https://example.org/bad#> .

ex:nA a vc:NodeAssertion ; vc:identifier "a" .
ex:nB a vc:NodeAssertion ; vc:identifier "b" .

ex:e1 a vc:EdgeAssertion ;
  vc:source ex:nA ;
  vc:target ex:nB .
""", format='turtle')
    with pytest.raises(CarrierShapeError):
        validate(g)


def test_node_missing_identifier_fails():
    g = Graph()
    g.parse(data="""
@prefix vc: <https://v4cat-oss.github.io/vcif-rdf/carrier#> .
@prefix ex: <https://example.org/bad#> .

ex:nA a vc:NodeAssertion ;
  vc:label "no identifier" .
""", format='turtle')
    with pytest.raises(CarrierShapeError):
        validate(g)


def test_edge_with_two_sources_fails():
    g = Graph()
    g.parse(data="""
@prefix vc: <https://v4cat-oss.github.io/vcif-rdf/carrier#> .
@prefix ex: <https://example.org/bad#> .

ex:nA a vc:NodeAssertion ; vc:identifier "a" .
ex:nB a vc:NodeAssertion ; vc:identifier "b" .
ex:nC a vc:NodeAssertion ; vc:identifier "c" .
ex:hasKind a vc:NodeAssertion ; vc:identifier "has-kind" .

ex:e1 a vc:EdgeAssertion ;
  vc:source ex:nA ;
  vc:source ex:nC ;
  vc:edgeKind ex:hasKind ;
  vc:target ex:nB .
""", format='turtle')
    with pytest.raises(CarrierShapeError):
        validate(g)
