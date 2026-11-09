#!/usr/bin/env python3
"""Immutable federation structure only; never proof, clean-Git or CBZ certification."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import signal
import stat
import subprocess
import sys
import tempfile
import tomllib
from datetime import datetime, timezone

from check_workspace import check_manifest
from verify_pins import load_pins
from verify_canonical_inputs import remote_repository, source_specs

REPOSITORIES = ('main', 'Math-', 'governance-', 'Universal-Law-Workspace', 'meta-framework',
    'query-', 'google-drive', 'trial', 'sandbox', 'd6g8k5htny-coder',
    'openclaw-custodian-validation', 'research-hosted-qualification')
MATH_PACKAGES = ('formal', 'frontiers/cap_first_exit_lean_20261002',
    'frontiers/determinant_moment_20261025', 'frontiers/source_derivative_gaussian_20261025',
    'frontiers/source_lifetime_realization_20261017', 'frontiers/source_smooth_realization_20261011',
    'specifications/lean_statement_proofs_20261011', 'specifications/lean_statements_20261010')
PACKAGE_ROOTS = {'main': ('formal',), 'Math-': MATH_PACKAGES}
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
CONTROL_LIMIT = 16 * 1024 * 1024
LISTING_LIMIT = 128 * 1024 * 1024
GIT_TIMEOUT = 60
CHILDREN = ('main', 'Math-', 'meta-framework', 'query-', 'google-drive', 'trial',
            'governance-', 'sandbox')
CANONICAL_KEYS = {'repository_registry', 'scientific_authority_map', 'downstream_gate', 'landing_claims'}


def require(condition, code):
    if not condition:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'DUPLICATE_JSON')
            result[key] = value
        return result
    def forbidden(_):
        raise ValueError('JSON_NUMBER')
    return json.loads(raw, object_pairs_hook=pairs, parse_float=forbidden, parse_constant=forbidden)


def _fingerprint(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _regular_bytes(path):
    require(path.resolve() == path and not path.is_symlink(), 'SELECTED_INPUT_SYMLINK')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode), 'SELECTED_INPUT_REGULAR')
        require(before.st_size <= CONTROL_LIMIT, 'CONTROL_SIZE')
        raw = bytearray()
        while True:
            chunk = os.read(fd, min(1024 * 1024, CONTROL_LIMIT + 1 - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
            require(len(raw) <= CONTROL_LIMIT, 'CONTROL_SIZE')
        require(len(raw) == before.st_size and _fingerprint(before) ==
                _fingerprint(os.fstat(fd)) == _fingerprint(path.lstat()), 'SELECTED_INPUT_DRIFT')
        return bytes(raw), _fingerprint(before)
    finally:
        os.close(fd)


def load_vector(path: Path) -> dict[str, str]:
    raw, _ = _regular_bytes(Path(path).absolute())
    data = strict_json(raw)
    require(type(data) is dict and set(data) == {'schema', 'repositories'} and
            data['schema'] == 'cbz.federation-vector.v1', 'VECTOR_SCHEMA')
    values = data['repositories']
    require(type(values) is dict and set(values) == set(REPOSITORIES), 'VECTOR_REPOSITORIES')
    require(all(type(value) is str and HEX40.fullmatch(value) for value in values.values()),
            'VECTOR_COMMIT')
    return values


def _read_env():
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
               GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0',
               GIT_OPTIONAL_LOCKS='0', GIT_ALLOW_PROTOCOL='', LC_ALL='C')
    return env


def read_git(repo: Path, args: tuple[str, ...], *, input_bytes: bytes | None = None) -> bytes:
    require(args and args[0] in ('rev-parse', 'ls-tree', 'ls-files', 'cat-file', 'config'), 'GIT_READ_OPERATION')
    if args[0] == 'config':
        require('--no-includes' in args and '--file' in args and args[-1] == '--list', 'GIT_READ_OPERATION')
    try:
        result = subprocess.run(['git', '-c', 'core.hooksPath=' + os.devnull,
            '-c', 'core.fsmonitor=false', '-c', 'core.untrackedCache=false', '-C', str(repo), *args],
            input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=_read_env(), timeout=GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        raise ValueError('GIT_READ_ERROR') from None
    require(result.returncode == 0, 'GIT_READ_FAILED')
    require(len(result.stdout) <= LISTING_LIMIT, 'GIT_READ_SIZE')
    return result.stdout


def _safe_path(path):
    require(type(path) is str and path and '\\' not in path and '\0' not in path and
            not path.startswith('/') and all(p not in ('', '.', '..', '.git')
                                            for p in path.split('/')), 'SOURCE_PATH')
    return path


def _tree(repo, commit):
    rows = {}
    for record in read_git(repo, ('ls-tree', '-r', '-z', '--full-tree', commit)).split(b'\0'):
        if not record:
            continue
        metadata, path = record.split(b'\t', 1)
        mode, kind, oid = metadata.decode('ascii').split(' ')
        require(mode in ('100644', '100755', '120000', '160000') and HEX40.fullmatch(oid)
                and kind == ('commit' if mode == '160000' else 'blob'), 'TREE_ENTRY')
        path = os.fsdecode(path)
        require(path not in rows, 'TREE_DUPLICATE')
        rows[path] = (mode, oid)
    return rows


def _index(repo):
    rows = {}
    raw = read_git(repo, ('ls-files', '--stage', '-z', '--full-name'))
    for record in raw.split(b'\0'):
        if not record:
            continue
        metadata, path = record.split(b'\t', 1)
        mode, oid, stage = metadata.decode('ascii').split(' ')
        path = os.fsdecode(path)
        require(stage == '0' and path not in rows, 'INDEX_CONFLICT')
        rows[path] = (mode, oid)
    return rows, sha(raw)


def read_blob(repo: Path, commit: str, path: str) -> dict:
    path = _safe_path(path)
    listing = read_git(repo, ('ls-tree', '-r', '-z', '--full-tree', commit, '--', ':(literal)' + path))
    entries = [row for row in listing.split(b'\0') if row]
    require(len(entries) == 1, 'SOURCE_BLOB_MISSING')
    meta, actual_path = entries[0].split(b'\t', 1)
    mode, kind, blob = meta.decode('ascii').split(' ')
    require(os.fsdecode(actual_path) == path and kind == 'blob' and mode in ('100644', '100755'),
            'SOURCE_BLOB_REGULAR')
    size = read_git(repo, ('cat-file', '-s', blob)).strip()
    require(size.isdigit() and int(size) <= CONTROL_LIMIT, 'CONTROL_SIZE')
    raw = read_git(repo, ('cat-file', 'blob', blob))
    require(len(raw) == int(size) and hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).
            hexdigest() == blob, 'SOURCE_BLOB_IDENTITY')
    return dict(commit=commit, path=path, mode=mode, blob=blob, bytes=len(raw), sha256=sha(raw), _raw=raw)


def capture_sources(root: Path, vector: dict[str, str]) -> dict:
    root = Path(root).absolute()
    require(root.is_dir() and root.resolve() == root, 'SOURCE_ROOT')
    require(set(vector) == set(REPOSITORIES), 'VECTOR_REPOSITORIES')
    repositories, selected = {}, {}
    for name in REPOSITORIES:
        repo = root / name
        require(repo.is_dir() and repo.resolve() == repo, 'SOURCE_CHECKOUT')
        actual = os.fsdecode(read_git(repo, ('rev-parse', '--show-toplevel')).rstrip(b'\n'))
        require(Path(actual).resolve() == repo, 'SOURCE_TOPLEVEL')
        require(read_git(repo, ('rev-parse', '--show-object-format')).strip() == b'sha1', 'SOURCE_FORMAT')
        head = read_git(repo, ('rev-parse', '--verify', 'HEAD^{commit}')).decode().strip()
        require(head == vector[name], 'HEAD_MISMATCH')
        require(read_git(repo, ('rev-parse', '--verify', vector[name] + '^{commit}')).decode().strip()
                == vector[name], 'SOURCE_COMMIT')
        tree_id = read_git(repo, ('rev-parse', vector[name] + '^{tree}')).decode().strip()
        tree = _tree(repo, vector[name])
        index, index_sha = _index(repo)
        require(index == tree, 'INDEX_TREE_MISMATCH')
        repositories[name] = dict(commit=head, tree=tree_id, index_sha256=index_sha,
                                  entries=len(tree), _path=repo, _tree=tree)
        paths = ['.gitmodules', 'pins.json', 'workspace/repositories.json'] if name == 'Universal-Law-Workspace' else []
        for package in PACKAGE_ROOTS.get(name, ()):
            paths += [package + '/lake-manifest.json', package + '/lean-toolchain']
            configs = [package + '/' + p for p in ('lakefile.toml', 'lakefile.lean')
                       if package + '/' + p in tree]
            require(configs, 'SELECTED_INPUT_CONFIG_MISSING')
            paths += configs
        for path in paths:
            binding = read_blob(repo, vector[name], path)
            raw, fingerprint = _regular_bytes(repo / path)
            require(raw == binding['_raw'], 'SELECTED_INPUT_MISMATCH')
            require(bool(fingerprint[2] & stat.S_IXUSR) == (binding['mode'] == '100755'),
                    'SELECTED_INPUT_MODE')
            selected[name + ':' + path] = dict(binding, repository=name, _fingerprint=fingerprint)
    return dict(repositories=repositories, selected=selected, _root=root, _vector=dict(vector),
                full_tracked_working_parity='NOT_ASSESSED', git_hygiene='NOT_ASSESSED')


def recheck_sources(snapshot):
    require(capture_sources(snapshot['_root'], snapshot['_vector']) == snapshot, 'SOURCE_DRIFT')


def _temporary(root):
    parent = Path(tempfile.gettempdir()).resolve()
    if parent.is_relative_to(root):
        parent = Path('/var/tmp').resolve()
    require(not parent.is_relative_to(root), 'EXTERNAL_TEMP_REQUIRED')
    return tempfile.TemporaryDirectory(prefix='cbz-vector-', dir=parent)


def _public(binding):
    return {key: value for key, value in binding.items() if not key.startswith('_')}


def verify_workspace(snapshot: dict) -> dict:
    name = 'Universal-Law-Workspace'
    selected = snapshot['selected']
    doc = strict_json(selected[name + ':workspace/repositories.json']['_raw'])
    require(type(doc) is dict and type(doc.get('canonical_inputs')) is dict and
            set(doc['canonical_inputs']) == CANONICAL_KEYS, 'CANONICAL_SET')
    require(type(doc.get('schema_version')) is int and not check_manifest(doc), 'WORKSPACE_MANIFEST')
    with _temporary(snapshot['_root']) as temporary:
        temp = Path(temporary)
        pins_path = temp/'pins.json'
        pins_path.write_bytes(selected[name + ':pins.json']['_raw'])
        pins, errors = load_pins(pins_path)
        require(not errors, 'WORKSPACE_PINS')
        modules_path = temp/'modules'
        modules_path.write_bytes(selected[name + ':.gitmodules']['_raw'])
        raw = read_git(temp, ('config', '--no-includes', '--null', '--file', str(modules_path), '--list'))
    modules = {}
    for record in raw.split(b'\0'):
        if not record:
            continue
        key, _, value = record.decode('utf-8').partition('\n')
        require(key.startswith('submodule.'), 'WORKSPACE_MODULES')
        section, _, field = key[len('submodule.'):].rpartition('.')
        require(section and field in ('path', 'url', 'branch', 'update'), 'WORKSPACE_MODULES')
        fields = modules.setdefault(section, {})
        require(field not in fields, 'WORKSPACE_MODULES_DUPLICATE')
        fields[field] = value
    by_path = {}
    for fields in modules.values():
        path = fields.get('path')
        require(path and path not in by_path, 'WORKSPACE_MODULES_DUPLICATE')
        by_path[path] = fields
    require(len(pins) == 8 and {p['name'] for p in pins} == set(CHILDREN), 'WORKSPACE_PIN_SET')
    expected_paths = {'repos/' + child for child in CHILDREN}
    links = {path: oid for path, (mode, oid) in snapshot['repositories'][name]['_tree'].items()
             if mode == '160000'}
    require(set(links) == expected_paths, 'WORKSPACE_GITLINK_SET')
    require(set(by_path) == expected_paths and {p['path'] for p in pins} == expected_paths,
            'WORKSPACE_MODULES_SET')
    pointers = []
    for pin in pins:
        child = pin['name']
        path = 'repos/' + child
        require(pin['path'] == path and links[path] == pin['pinned_sha'] == snapshot['_vector'][child],
                'WORKSPACE_PIN_IDENTITY')
        mod = by_path[path]
        require(pin['url'] == mod.get('url') == 'https://github.com/d6g8k5htny-coder/' + child + '.git'
                and type(pin['default_branch']) is str and pin['default_branch']
                and mod.get('branch') == pin['default_branch']
                and (mod.get('update') == 'none') == pin['opt_in'], 'WORKSPACE_MODULES_IDENTITY')
        pointers.append(dict(repository=child, path=path, commit=links[path]))
    canonical = []
    for key, repository, url, path, commit, blob, binding in source_specs(doc, pins):
        short = repository.split('/', 1)[1]
        require(short in snapshot['repositories'], 'CANONICAL_REPOSITORY')
        require(read_git(snapshot['repositories'][short]['_path'],
                         ('cat-file', '-t', commit)).strip() == b'commit', 'CANONICAL_COMMIT')
        actual = read_blob(snapshot['repositories'][short]['_path'], commit, path)
        require(actual['blob'] == blob, 'CANONICAL_BLOB')
        canonical.append(dict(_public(actual), key=key, repository=short, url=url, binding=binding))
    return dict(pointers=sorted(pointers, key=lambda p: p['repository']),
                canonical=sorted(canonical, key=lambda p: p['key']))


def _remote_url(url):
    try:
        return 'https://github.com/' + remote_repository(url)
    except (ValueError, TypeError):
        raise ValueError('REMOTE_URL') from None


def verify_locks(snapshot: dict) -> dict:
    locks, toolchains, packages = {}, set(), []
    for repository, roots in PACKAGE_ROOTS.items():
        for package in roots:
            key = repository + ':' + package
            bound = snapshot['selected'][key + '/lake-manifest.json']
            data = strict_json(bound['_raw'])
            require(type(data) is dict and set(data) == {'version', 'packagesDir', 'packages',
                    'name', 'lakeDir', 'fixedToolchain'} and data['version'] == '1.2.0'
                    and type(data['packages']) is list and type(data['name']) is str
                    and data['name'] and type(data['fixedToolchain']) is bool, 'LOCK_SCHEMA')
            _safe_path(data['packagesDir']); _safe_path(data['lakeDir'])
            toolchain = snapshot['selected'][key + '/lean-toolchain']['_raw'].decode('utf-8').strip()
            require(re.fullmatch(r'leanprover/lean4:v[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?', toolchain),
                    'LOCK_TOOLCHAIN')
            toolchains.add(toolchain)
            locks[key] = data
            packages.append(dict(repository=repository, root=package, recorded_lock_name=data['name'],
                configuration_semantics='NOT_ASSESSED', lock=_public(bound), toolchain=toolchain,
                fixed_toolchain=data['fixedToolchain']))
    require(len(toolchains) == 1, 'LOCK_TOOLCHAIN_DRIFT')
    git_dependencies, path_dependencies, identities = [], [], {}
    for key, data in locks.items():
        repository, package = key.split(':', 1)
        seen = set()
        for dependency in data['packages']:
            require(type(dependency) is dict and dependency.get('type') in ('git', 'path'),
                    'LOCK_DEPENDENCY_TYPE')
            name = dependency.get('name')
            require(type(name) is str and name and name not in seen, 'LOCK_DEPENDENCY_DUPLICATE')
            seen.add(name)
            common = {'type', 'name', 'inherited', 'configFile', 'manifestFile'}
            required = common | ({'scope', 'url', 'rev', 'inputRev', 'subDir'}
                                 if dependency['type'] == 'git' else {'dir'})
            require(set(dependency) == required and type(dependency['inherited']) is bool,
                    'LOCK_DEPENDENCY_SCHEMA')
            _safe_path(dependency['configFile']); _safe_path(dependency['manifestFile'])
            if dependency['type'] == 'git':
                require(type(dependency['rev']) is str and HEX40.fullmatch(dependency['rev']), 'LOCK_COMMIT')
                require(type(dependency['scope']) is str and type(dependency['inputRev']) is str
                        and dependency['inputRev'], 'LOCK_DEPENDENCY_SCHEMA')
                if dependency['subDir'] is not None:
                    _safe_path(dependency['subDir'])
                url = _remote_url(dependency['url'])
                identity = (url, dependency['rev'], dependency['subDir'])
                require(name not in identities or identities[name] == identity, 'LOCK_DEPENDENCY_DRIFT')
                identities[name] = identity
                git_dependencies.append(dict(repository=repository, package=package, name=name,
                    url=url, source_url=dependency['url'], commit=dependency['rev'], subdirectory=dependency['subDir']))
            else:
                relative = dependency['dir']
                require(type(relative) is str and relative and '\\' not in relative and '\0' not in relative
                        and not relative.startswith('/'), 'LOCK_PATH_TARGET')
                require(relative == posixpath.normpath(relative), 'LOCK_PATH_TARGET')
                target = posixpath.normpath(package + '/' + relative)
                require(target in PACKAGE_ROOTS[repository], 'LOCK_PATH_TARGET')
                target_key = repository + ':' + target
                require(locks[target_key]['name'] == name, 'LOCK_PATH_NAME')
                for field in ('configFile', 'manifestFile'):
                    require(target_key + '/' + dependency[field] in snapshot['selected'], 'LOCK_PATH_BINDING')
                require(dependency['configFile'] == 'lakefile.toml', 'LOCK_PATH_CONFIG_FORMAT')
                target_config = tomllib.loads(snapshot['selected'][target_key + '/lakefile.toml']['_raw'].decode('utf-8'))
                require(type(target_config.get('name')) is str and target_config['name'] == name,
                        'LOCK_PATH_CONFIG_NAME')
                path_dependencies.append(dict(repository=repository, package=package,
                    name=name, directory=relative, target=target, target_toml_name=target_config['name']))
    return dict(packages=packages, git_dependencies=git_dependencies,
                path_dependencies=path_dependencies, toolchain=next(iter(toolchains)))


def required_remote_commits(snapshot: dict, workspace: dict, locks: dict) -> list[dict]:
    requests = {}
    def add(url, commit, role):
        url = _remote_url(url)
        require(type(commit) is str and HEX40.fullmatch(commit), 'REMOTE_COMMIT')
        requests.setdefault((url, commit), []).append(role)
    for name, commit in snapshot['_vector'].items():
        add('https://github.com/d6g8k5htny-coder/' + name, commit, 'source:' + name)
    for row in workspace['canonical']:
        add(row['url'], row['commit'], 'canonical:' + row['key'])
    for row in locks['git_dependencies']:
        add(row['url'], row['commit'], 'dependency:' + row['repository'] + ':' + row['package'] + ':' + row['name'])
    return [dict(url=url, commit=commit, roles=sorted(set(roles)))
            for (url, commit), roles in sorted(requests.items())]


def _now():
    return datetime.now(timezone.utc).isoformat()


def _network_env():
    trusted_transport = {'GIT_SSL_CAINFO', 'GIT_SSL_CAPATH', 'GIT_PROXY_SSL_CAINFO', 'GIT_ASKPASS'}
    env = {key: value for key, value in os.environ.items()
           if not key.startswith('GIT_') or key in trusted_transport}
    env.update(GIT_TERMINAL_PROMPT='0', GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1',
               GIT_OPTIONAL_LOCKS='0', GIT_ALLOW_PROTOCOL='https', LC_ALL='C')
    return env


def _network_process(command, env, *, timeout=GIT_TIMEOUT):
    process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except OSError:
            try:
                process.kill()
            except OSError:
                raise ValueError('NETWORK_CLEANUP_ERROR') from None
        try:
            process.communicate(timeout=1)
        except (OSError, subprocess.SubprocessError):
            raise ValueError('NETWORK_CLEANUP_ERROR') from None
        raise
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def fetch_exact_commit(request: dict, storage: Path) -> dict:
    url = _remote_url(request['url'])
    commit = request['commit']
    require(type(commit) is str and HEX40.fullmatch(commit), 'REMOTE_COMMIT')
    storage = Path(storage).absolute()
    require(storage.resolve() == storage, 'NETWORK_STORAGE')
    storage.mkdir(parents=True, exist_ok=True, mode=0o700)
    bare = storage / sha(url.encode())[:32]
    env = _network_env()
    command = ['git', '-c', 'core.hooksPath=' + os.devnull, '-c', 'core.fsmonitor=false',
               '-c', 'gc.auto=0', '-c', 'maintenance.auto=false', '-c', 'fetch.fsckObjects=true']
    result = dict(url=url, commit=commit, roles=list(request.get('roles', [])),
                  status='FETCH_FAILED', exit_code=None, started_utc=_now())
    try:
        if not bare.exists():
            initialized = _network_process([*command, 'init', '--bare', '--quiet', '--template=', str(bare)], env)
            if initialized.returncode != 0:
                result.update(status='SETUP_FAILED', exit_code=initialized.returncode)
                return result
        require(bare.resolve() == bare and bare.is_dir(), 'NETWORK_STORAGE')
        observed = _network_process([*command, '--git-dir=' + str(bare), 'fetch',
            '--depth=1', '--no-tags', '--filter=blob:none', '--no-recurse-submodules',
            '--no-auto-maintenance', '--no-write-fetch-head', '--', url, commit], env)
        result.update(exit_code=observed.returncode,
            diagnostic_bytes=len(observed.stdout) + len(observed.stderr),
            diagnostic_sha256=sha(observed.stdout + b'\0' + observed.stderr))
        if observed.returncode == 0:
            try:
                actual = read_git(bare, ('rev-parse', '--verify', commit + '^{commit}')).decode().strip()
            except ValueError:
                actual = None
            result['status'] = 'FETCHED_COMMIT' if actual == commit else 'IDENTITY_MISMATCH'
    except subprocess.TimeoutExpired:
        result['status'] = 'TIMEOUT'
    except ValueError as error:
        result['status'] = 'CLEANUP_ERROR' if error.args == ('NETWORK_CLEANUP_ERROR',) else 'TRANSPORT_ERROR'
        if result['status'] == 'CLEANUP_ERROR':
            result['error_code'] = 'NETWORK_CLEANUP_ERROR'
    except (OSError, subprocess.SubprocessError):
        result['status'] = 'TRANSPORT_ERROR'
    finally:
        result['finished_utc'] = _now()
    return result


def _source_identity():
    paths = {'verifier': Path(__file__)}
    for function in (check_manifest, load_pins, source_specs):
        paths[function.__module__] = Path(sys.modules[function.__module__].__file__)
    return {name: sha(path.read_bytes()) for name, path in sorted(paths.items())}


def _error_code(error):
    value = str(error) if type(error) is ValueError else ''
    return value if re.fullmatch(r'[A-Z][A-Z0-9_]{0,63}', value) else 'STRUCTURE_ERROR'


def verify(root: Path, vector_path: Path, *, network: bool = False, fetcher=None) -> dict:
    report = dict(schema='cbz.federation-vector-verification.v1', status='FAIL',
        certification_scope='federation-vector-structural-integrity-only',
        cbz_green=False, semantic_claim_completeness=False,
        full_tracked_working_parity='NOT_ASSESSED', git_hygiene='NOT_ASSESSED',
        started_utc=_now(), errors=[], network=dict(status='NOT_REQUESTED', observations=[]))
    snapshot = None
    before_vector = None
    control_stage = True
    try:
        identity = _source_identity()
        report['source_sha256'] = identity
        report['python'] = sys.version.split()[0]
        version = subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 timeout=GIT_TIMEOUT, env=_read_env())
        require(version.returncode == 0, 'GIT_VERSION')
        report['git_version'] = version.stdout.decode('ascii').strip()
        vector_path = Path(vector_path).absolute()
        raw, before_vector = _regular_bytes(vector_path)
        report['vector_sha256'] = sha(raw)
        vector = load_vector(vector_path)
        control_stage = False
        snapshot = capture_sources(root, vector)
        report['repositories'] = {name: _public(row) for name, row in snapshot['repositories'].items()}
        report['selected_inputs'] = [_public(row) for row in snapshot['selected'].values()]
        workspace = verify_workspace(snapshot)
        locks = verify_locks(snapshot)
        report.update(workspace=workspace, locks=locks)
        if network:
            report['network']['status'] = 'FAIL'
            requests = required_remote_commits(snapshot, workspace, locks)
            with _temporary(snapshot['_root']) as temporary:
                for request in requests:
                    try:
                        observation = (fetcher or fetch_exact_commit)(request, Path(temporary))
                        require(type(observation) is dict and observation.get('url') == request['url']
                                and observation.get('commit') == request['commit'], 'NETWORK_OBSERVATION')
                    except Exception:
                        observation = dict(request, status='TRANSPORT_ERROR', exit_code=None)
                    report['network']['observations'].append(observation)
                    if observation['status'] == 'CLEANUP_ERROR':
                        break
            require(all(row['status'] == 'FETCHED_COMMIT' for row in report['network']['observations']),
                    'NETWORK_REQUIRED_FAILURE')
            report['network']['status'] = 'PASS'
    except Exception as error:
        report['errors'].append(_error_code(error))
        report['control_input_error'] = control_stage
    finally:
        if snapshot is not None:
            try:
                recheck_sources(snapshot)
                after_raw, after_vector = _regular_bytes(Path(vector_path).absolute())
                require(before_vector == after_vector and sha(after_raw) == report['vector_sha256'], 'VECTOR_DRIFT')
                require(_source_identity() == report['source_sha256'], 'VERIFIER_SOURCE_DRIFT')
            except Exception as error:
                report['errors'].append(_error_code(error))
        report['finished_utc'] = _now()
    if not report['errors']:
        report['status'] = 'PASS'
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--vector', type=Path, required=True)
    parser.add_argument('--network', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    output = None
    try:
        if args.output is not None:
            destination = args.output.absolute()
            require(destination.resolve() == destination and not destination.is_symlink(), 'OUTPUT_PATH')
            for name in REPOSITORIES:
                require(not destination.is_relative_to((args.root/name).resolve()), 'OUTPUT_IN_SOURCE')
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            output = os.fdopen(fd, 'w', encoding='ascii')
        report = verify(args.root, args.vector, network=args.network)
        raw = json.dumps(report, ensure_ascii=True, sort_keys=True, allow_nan=False) + '\n'
        if output:
            output.write(raw)
            output.flush()
            print(json.dumps(dict(status=report['status'], cbz_green=False)))
        else:
            print(raw, end='')
        return 0 if report['status'] == 'PASS' else 2 if report.get('control_input_error') else 1
    except (ValueError, OSError):
        print(json.dumps(dict(status='FAIL', error='OUTPUT_SETUP', cbz_green=False)), file=sys.stderr)
        return 2
    finally:
        if output:
            output.close()


if __name__ == '__main__':
    raise SystemExit(main())
