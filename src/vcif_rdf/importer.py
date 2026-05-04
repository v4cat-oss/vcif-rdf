"""
vcif_rdf.importer — apply mode.

Walk the data graph, extract NodeAssertions and EdgeAssertions,
mutate the v4cat catalogue exclusively through the public ISA
(introduce_node, edge). Idempotent: re-importing produces the
same end-state.

The importer is a *boring loop* — exactly what theory.md § 15
implies: a v4cat run is a composition of left-translations in `H`,
and the importer is just that composition expressed against rdflib
results.
"""
from __future__ import annotations

import sqlite3
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

VC = 'https://v4cat-oss.github.io/vcif-rdf/carrier#'
VC_NodeAssertion = URIRef(VC + 'NodeAssertion')
VC_EdgeAssertion = URIRef(VC + 'EdgeAssertion')
VC_identifier = URIRef(VC + 'identifier')
VC_label = URIRef(VC + 'label')
VC_source = URIRef(VC + 'source')
VC_edgeKind = URIRef(VC + 'edgeKind')
VC_target = URIRef(VC + 'target')


def apply(data: Graph, catalogue) -> dict:
    """Apply the data graph to the catalogue via public ISA verbs.

    Returns a counts report.
    """
    report = {
        'nodes_added': 0,
        'nodes_skipped': 0,
        'edges_added': 0,
        'edges_skipped': 0,
    }

    # 1. NodeAssertions -> introduce_node
    for node in data.subjects(RDF.type, VC_NodeAssertion):
        ident = data.value(node, VC_identifier)
        label = data.value(node, VC_label)
        if ident is None:
            continue
        node_id = str(ident)
        node_label = str(label) if label is not None else node_id
        # Each carrier-level node is imported as a v4cat node of kind
        # `vc:NodeAssertion` itself a node-kind. The importer doesn't
        # synthesize per-domain kinds; that's the document author's
        # responsibility (via has-kind edges).
        kind = 'vcif-rdf.NodeAssertion'
        try:
            catalogue.introduce_node(node_id, node_label, kind)
            report['nodes_added'] += 1
        except sqlite3.IntegrityError:
            report['nodes_skipped'] += 1
        except ValueError:
            # Unknown node-type; skip but count
            report['nodes_skipped'] += 1

    # 2. EdgeAssertions -> edge
    for edge in data.subjects(RDF.type, VC_EdgeAssertion):
        source = data.value(edge, VC_source)
        kind_node = data.value(edge, VC_edgeKind)
        target = data.value(edge, VC_target)
        if source is None or kind_node is None or target is None:
            report['edges_skipped'] += 1
            continue
        source_id = str(data.value(source, VC_identifier) or source)
        target_id = str(data.value(target, VC_identifier) or target)
        kind_id = str(data.value(kind_node, VC_identifier) or kind_node)
        try:
            catalogue.edge(source_id, target_id, kind_id)
            report['edges_added'] += 1
        except sqlite3.IntegrityError:
            report['edges_skipped'] += 1
        except (ValueError, RuntimeError):
            report['edges_skipped'] += 1

    return report
