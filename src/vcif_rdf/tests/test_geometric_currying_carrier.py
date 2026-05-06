"""
Tests for the gc-vcif-rdf-carrier sub-fire.

Closes vcif-rdf#1. Verifies the new HF-GeometricCurrying carrier
classes + slots load cleanly into the carrier graph.
"""
from __future__ import annotations

from vcif_rdf.ontology_loader import carrier_graph


def test_event_cell_assertion_loaded():
    g = carrier_graph()
    iris = {str(s) for s in g.subjects()}
    assert any('EventCellAssertion' in i for i in iris)


def test_role_binding_loaded():
    g = carrier_graph()
    iris = {str(s) for s in g.subjects()}
    assert any('carrier-class:RoleBinding' in str(o) for o in g.objects()) or \
           any('RoleBinding' in i for i in iris)


def test_geometric_carrier_slots_loaded():
    g = carrier_graph()
    iris = {str(s) for s in g.subjects()}
    for slot in ('cellKind', 'role', 'occupant', 'roleOfCell', 'closureState'):
        assert any(slot in i for i in iris), f"slot {slot!r} not declared"


def test_existing_cell_assertion_preserved():
    """Per the migration shadow, the existing vc:CellAssertion (kquery
    cell) is NOT renamed in this sub-fire. It must continue to load."""
    g = carrier_graph()
    iris = {str(s) for s in g.subjects()}
    assert any('CellAssertion' in i and 'EventCellAssertion' not in i
               for i in iris)
