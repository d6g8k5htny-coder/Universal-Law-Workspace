"""Public re-exports for the Universal Law workspace. No implementation lives here.

This package is a **thin, documented front door** to code that lives in the
submodules under ``repos/``. It re-exports; it does not reimplement, vendor or fork.
Everything it exposes comes from ``repos/query-``, whose bytes are pinned by the
submodule gitlink.

Scientific effect: NONE. Importing this package reads no claim register and moves no
theorem, lemma, prize or bound. A successful import proves the submodules are
initialised, nothing more.

Usage from a fresh clone::

    git clone --recurse-submodules https://github.com/d6g8k5htny-coder/universal-law-workspace
    cd universal-law-workspace
    PYTHONPATH=src python3 -c "import universal_law_workspace as w; print(w.entry_points())"

If the submodules are not initialised, every accessor raises
:class:`WorkspaceNotInitialised` with the exact command to fix it, rather than a bare
``ImportError`` that leaves you guessing.
"""
from __future__ import annotations

import pathlib
import sys

__all__ = ['ROOT', 'WorkspaceNotInitialised', 'query_package', 'entry_points',
           'documented_checks']

ROOT = pathlib.Path(__file__).resolve().parents[2]

#: Where the query package's canonical source lives, once PR #16 (or its successor) is
#: on the query- ref this workspace pins. On query- `main` as of this writing there is
#: no src/ tree at all, which is exactly what that PR fixes.
_QUERY_SRC = ROOT / 'repos' / 'query-' / 'src'


class WorkspaceNotInitialised(RuntimeError):
    """Raised when a submodule this accessor needs has not been checked out."""


def _require_query_src() -> pathlib.Path:
    if not (_QUERY_SRC / 'universal_law_query' / '__init__.py').is_file():
        raise WorkspaceNotInitialised(
            f'{_QUERY_SRC} has no universal_law_query package.\n'
            'If the submodules are not initialised:\n'
            '    git submodule update --init --recursive\n'
            'If they are, then the query- ref this workspace pins predates the src/\n'
            'migration. See BRANCH_MAP.md: query- main has no src/ tree; the tree is on\n'
            'integration/public-src-20260926 (PR #16). Fetch the named branches with\n'
            '    scripts/fetch_named_branches.sh\n'
            'and check that ref out inside repos/query-.')
    return _QUERY_SRC


def query_package():
    """Return the ``universal_law_query`` module from the pinned ``query-`` submodule."""
    src = _require_query_src()
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    import universal_law_query  # noqa: PLC0415  (deliberate: after path setup)
    return universal_law_query


def entry_points() -> dict[str, str]:
    """The documented public entry points, as path strings relative to this repository.

    Returned as strings rather than imported callables so this is answerable without
    initialising anything -- a map you can read before you have a checkout.
    """
    return {
        'query lookup CLI (package)': 'repos/query-/src/universal_law_query/cli.py',
        'query lookup CLI (wrapper)': 'repos/query-/research_query.py',
        'catalog entry helper': 'repos/query-/catalog_entry_helper.py',
        'portable stub verifier': 'repos/query-/verify_portable_stubs.py',
        'public catalog': 'repos/meta-framework/registry.json',
        'cross-repository federation controls': 'repos/trial/federation/test_federation.py',
        'bounded public replay': 'repos/trial/federation/replay.py',
        'downstream hard gate': 'repos/Math-/frontiers/downstream_gate_20260925/hard_gate.py',
    }


def documented_checks() -> list[dict[str, str]]:
    """The checks the README tells a stranger to run, with what each one does NOT prove."""
    return [
        {'name': 'query legacy controls',
         'cwd': 'repos/query-',
         'command': "python3 -B -S -m unittest test_research_query.py test_catalog_entry_helper.py test_verify_portable_stubs.py",
         'does_not_prove': 'that the catalog is current or that any artifact is accepted'},
        {'name': 'query package controls',
         'cwd': 'repos/query-',
         'command': "python3 -B -S -m unittest discover -s tests -p 'test_*.py'",
         'does_not_prove': 'anything mathematical; these are packaging and custody controls',
         'note': 'requires the src/ tree -- see BRANCH_MAP.md on query- main vs PR #16'},
        {'name': 'portable stub identities + Math- tip drift',
         'cwd': 'repos/query-',
         'command': 'python3 -B -S verify_portable_stubs.py --check-math-tip',
         'does_not_prove': 'that the gate those bytes implement is sound; it compares bytes',
         'note': 'needs outbound access to raw.githubusercontent.com'},
        {'name': 'cross-repository federation controls',
         'cwd': 'repos/trial/federation',
         'command': 'FEDERATION_WORKSPACE=$PWD/../../.. python3 -B -S -m unittest test_federation',
         'does_not_prove': 'acceptance of any catalog artifact; it checks lookup, custody and the public/private boundary'},
    ]
