"""SPARQL kquery tests — V₄ cell classification on RDF data."""
from __future__ import annotations

from rdflib import Graph, URIRef

from vcif_rdf import cells


def _ex(name: str) -> URIRef:
    return URIRef('https://example.org/hf-dbe#' + name)


def test_hf_dbe_kquery_eleven_only(hf_dbe_closure_graph):
    """For the canonical HF-DBE closure: 00=01=10 empty, 11=[claim]."""
    cover = _ex('cover')
    in_set = _ex('inSet')
    result = cells(hf_dbe_closure_graph, cover, in_set)
    # Identify the claim node IRI
    claim = _ex('claimDbeShadows')
    assert claim in result['11']
    assert result['00'] == []
    assert result['01'] == []
    assert result['10'] == []


def test_disjoint_observers_yield_10_and_01():
    """A cover whose left and right are disjoint and partition U gives
    no 11 cell and a complementary 10 + 01 split."""
    g = Graph()
    g.parse(data="""
@prefix vc: <https://v4cat-oss.github.io/vcif-rdf/carrier#> .
@prefix ex: <https://example.org/test#> .

ex:inSet a vc:NodeAssertion ; vc:identifier "in-set" .
ex:U a vc:NodeAssertion ; vc:identifier "U" .
ex:A a vc:NodeAssertion ; vc:identifier "A" .
ex:B a vc:NodeAssertion ; vc:identifier "B" .

ex:u1 a vc:NodeAssertion ; vc:identifier "u1" .
ex:u2 a vc:NodeAssertion ; vc:identifier "u2" .

ex:m1 a vc:EdgeAssertion ; vc:source ex:u1 ; vc:edgeKind ex:inSet ; vc:target ex:U .
ex:m2 a vc:EdgeAssertion ; vc:source ex:u2 ; vc:edgeKind ex:inSet ; vc:target ex:U .

ex:m3 a vc:EdgeAssertion ; vc:source ex:u1 ; vc:edgeKind ex:inSet ; vc:target ex:A .
ex:m4 a vc:EdgeAssertion ; vc:source ex:u2 ; vc:edgeKind ex:inSet ; vc:target ex:B .

ex:cover a vc:CoverAssertion ;
  vc:identifier "test-cover" ;
  vc:universe ex:U ;
  vc:leftObserver ex:A ;
  vc:rightObserver ex:B .
""", format='turtle')
    cover = URIRef('https://example.org/test#cover')
    in_set = URIRef('https://example.org/test#inSet')
    result = cells(g, cover, in_set)

    u1 = URIRef('https://example.org/test#u1')
    u2 = URIRef('https://example.org/test#u2')
    assert u1 in result['10']
    assert u2 in result['01']
    assert result['11'] == []
    assert result['00'] == []


def test_blind_member_lands_in_00():
    """A member of U not in A or B lands in cell 00."""
    g = Graph()
    g.parse(data="""
@prefix vc: <https://v4cat-oss.github.io/vcif-rdf/carrier#> .
@prefix ex: <https://example.org/test#> .

ex:inSet a vc:NodeAssertion ; vc:identifier "in-set" .
ex:U a vc:NodeAssertion ; vc:identifier "U" .
ex:A a vc:NodeAssertion ; vc:identifier "A" .
ex:B a vc:NodeAssertion ; vc:identifier "B" .

ex:blind a vc:NodeAssertion ; vc:identifier "blind" .

ex:m1 a vc:EdgeAssertion ; vc:source ex:blind ; vc:edgeKind ex:inSet ; vc:target ex:U .

ex:cover a vc:CoverAssertion ;
  vc:identifier "test-cover" ;
  vc:universe ex:U ;
  vc:leftObserver ex:A ;
  vc:rightObserver ex:B .
""", format='turtle')
    cover = URIRef('https://example.org/test#cover')
    in_set = URIRef('https://example.org/test#inSet')
    result = cells(g, cover, in_set)
    blind = URIRef('https://example.org/test#blind')
    assert blind in result['00']
