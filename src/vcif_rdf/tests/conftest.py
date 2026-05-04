"""Shared fixtures for vcif-rdf tests."""
from __future__ import annotations

from pathlib import Path

import pytest
from rdflib import Graph, URIRef

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLES_DIR = REPO_ROOT / 'docs' / 'examples'

VC = 'https://v4cat-oss.github.io/vcif-rdf/carrier#'


def _load_ttl(name: str) -> Graph:
    g = Graph()
    g.parse((EXAMPLES_DIR / name).as_posix(), format='turtle')
    return g


@pytest.fixture
def agda_import_graph() -> Graph:
    return _load_ttl('agda-import.ttl')


@pytest.fixture
def hf_dbe_closure_graph() -> Graph:
    return _load_ttl('hf-dbe-closure.ttl')


@pytest.fixture
def minimal_snapshot() -> Graph:
    """A minimal carrier-conformant snapshot with two nodes + one edge."""
    g = Graph()
    g.parse(data="""
@prefix vc: <https://v4cat-oss.github.io/vcif-rdf/carrier#> .
@prefix ex: <https://example.org/test#> .

ex:nA a vc:NodeAssertion ;
  vc:identifier "a" ; vc:label "A" .

ex:nB a vc:NodeAssertion ;
  vc:identifier "b" ; vc:label "B" .

ex:hasKind a vc:NodeAssertion ;
  vc:identifier "has-kind" ; vc:label "has-kind" .

ex:e1 a vc:EdgeAssertion ;
  vc:source ex:nA ; vc:edgeKind ex:hasKind ; vc:target ex:nB .
""", format='turtle')
    return g
