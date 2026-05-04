"""
vcif_rdf.ontology_loader — read the canonical RDF + SHACL + SPARQL
files from package data via importlib.resources.

The ontology and shape graphs are themselves data — they ship with the
package and are not touched at runtime. This module exposes them as
parsed `rdflib.Graph` objects (for the ontology + shapes) and as raw
SPARQL strings (for the queries).
"""
from __future__ import annotations

from functools import lru_cache
from importlib.resources import files

from rdflib import Graph

_PKG = files('vcif_rdf')

CARRIER_TTL = 'ontology/carrier.ttl'

PROFILE_FILES = {
    'v4cat.snapshot':            'ontology/profiles/snapshot.ttl',
    'v4cat.patch':               'ontology/profiles/patch.ttl',
    'v4cat.vocabulary':          'ontology/profiles/vocabulary.ttl',
    'v4cat.recognizer-package':  'ontology/profiles/recognizer-package.ttl',
    'v4cat.closure-report':      'ontology/profiles/closure-report.ttl',
    'v4cat.residue-report':      'ontology/profiles/residue-report.ttl',
}

SHAPE_FILES = (
    'shapes/carrier-form.ttl',
    'shapes/carrier-self-hosting.ttl',
)

KQUERY_RQ = 'queries/kquery.rq'


@lru_cache(maxsize=None)
def carrier_graph() -> Graph:
    """The vc: carrier ontology (carrier.ttl) parsed as an rdflib Graph."""
    g = Graph()
    g.parse(data=(_PKG / CARRIER_TTL).read_text(), format='turtle')
    return g


@lru_cache(maxsize=None)
def profile_graph(kind: str) -> Graph:
    """The profile-specific ontology graph for the given top-level kind."""
    if kind not in PROFILE_FILES:
        raise ValueError(
            f"unknown vcif-rdf kind {kind!r}; expected one of "
            f"{sorted(PROFILE_FILES)}"
        )
    g = Graph()
    g.parse(data=(_PKG / PROFILE_FILES[kind]).read_text(), format='turtle')
    return g


@lru_cache(maxsize=None)
def shapes_graph() -> Graph:
    """Combined SHACL Core + SHACL-SPARQL shapes graph."""
    g = Graph()
    for path in SHAPE_FILES:
        g.parse(data=(_PKG / path).read_text(), format='turtle')
    # The shapes also need the carrier ontology in scope so sh:class
    # references resolve.
    g += carrier_graph()
    return g


@lru_cache(maxsize=None)
def kquery_template() -> str:
    """Raw SPARQL SELECT template for kquery. Substitute $cover and
    $inSetKind via initBindings when executing against a data graph."""
    return (_PKG / KQUERY_RQ).read_text()
