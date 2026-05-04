"""Ontology + shapes loader smoke tests — every shipped .ttl parses."""
from __future__ import annotations

import pytest

from vcif_rdf.ontology_loader import (
    PROFILE_FILES,
    carrier_graph,
    profile_graph,
    shapes_graph,
    kquery_template,
)


def test_carrier_graph_loads():
    g = carrier_graph()
    # at minimum, vc:NodeAssertion / vc:EdgeAssertion are declared
    iris = {str(s) for s in g.subjects()}
    assert any('NodeAssertion' in i for i in iris)
    assert any('EdgeAssertion' in i for i in iris)


@pytest.mark.parametrize('kind', list(PROFILE_FILES))
def test_profile_graph_loads(kind: str):
    g = profile_graph(kind)
    assert len(g) > 0


def test_shapes_graph_loads():
    g = shapes_graph()
    # Must contain at least the EdgeAssertionShape's three property
    # constraints. Loose check: nontrivial size.
    assert len(g) > 20


def test_kquery_template_is_sparql():
    text = kquery_template()
    assert 'SELECT ?u ?cell' in text
    assert 'vc:cell11' in text
    assert 'vc:cell00' in text
