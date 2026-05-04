"""
vcif_rdf.cli — console-script entry point.

Subcommands:

    vcif-rdf validate <doc.ttl>                          SHACL Core + SHACL-SPARQL
    vcif-rdf inspect <doc.ttl>                           parse + print structure
    vcif-rdf dry-run --catalogue <db> <doc.ttl>          report proposed mutations
    vcif-rdf import --catalogue <db> <doc.ttl>           apply via v4cat public API
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rdflib import Graph

from . import parse as _parse, validate as _validate, apply as _apply
from .validator import CarrierShapeError


def _load(path: str) -> Graph:
    return _parse(path)


def _cmd_validate(args: argparse.Namespace) -> int:
    g = _load(args.doc)
    try:
        _validate(g)
    except CarrierShapeError as e:
        print(f'SHACL validation failed:\n{e.results_text}', file=sys.stderr)
        return 2
    n_nodes = len(list(g.triples((None, None, None))))
    print(f'{args.doc}: OK ({n_nodes} triples)')
    return 0


def _cmd_inspect(args: argparse.Namespace) -> int:
    from rdflib.namespace import RDF
    from .importer import VC_NodeAssertion, VC_EdgeAssertion
    g = _load(args.doc)
    n_nodes = len(list(g.subjects(RDF.type, VC_NodeAssertion)))
    n_edges = len(list(g.subjects(RDF.type, VC_EdgeAssertion)))
    print(f'NodeAssertions: {n_nodes}')
    print(f'EdgeAssertions: {n_edges}')
    print(f'Total triples:  {len(list(g.triples((None, None, None))))}')
    return 0


def _cmd_dry_run(args: argparse.Namespace) -> int:
    from rdflib.namespace import RDF
    from .importer import VC_NodeAssertion, VC_EdgeAssertion
    g = _load(args.doc)
    _validate(g)
    n_nodes = len(list(g.subjects(RDF.type, VC_NodeAssertion)))
    n_edges = len(list(g.subjects(RDF.type, VC_EdgeAssertion)))
    print(f'dry-run plan ({args.doc} → {args.catalogue}):')
    print(f'  introduce_node × {n_nodes}')
    print(f'  edge × {n_edges}')
    return 0


def _cmd_import(args: argparse.Namespace) -> int:
    from v4cat import SymmetryCatalogue
    g = _load(args.doc)
    _validate(g)
    with SymmetryCatalogue(args.catalogue) as cat:
        report = _apply(g, cat)
    for k, v in report.items():
        print(f'  {k:25s} {v}')
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='vcif-rdf', description='vcif-rdf CLI')
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_validate = sub.add_parser('validate', help='SHACL Core + SHACL-SPARQL')
    p_validate.add_argument('doc')
    p_validate.set_defaults(fn=_cmd_validate)

    p_inspect = sub.add_parser('inspect', help='parse + print structure')
    p_inspect.add_argument('doc')
    p_inspect.set_defaults(fn=_cmd_inspect)

    p_dry = sub.add_parser('dry-run', help='report proposed mutations')
    p_dry.add_argument('--catalogue', required=True)
    p_dry.add_argument('doc')
    p_dry.set_defaults(fn=_cmd_dry_run)

    p_import = sub.add_parser('import', help='apply via v4cat public API')
    p_import.add_argument('--catalogue', required=True)
    p_import.add_argument('doc')
    p_import.set_defaults(fn=_cmd_import)

    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == '__main__':
    sys.exit(main())
