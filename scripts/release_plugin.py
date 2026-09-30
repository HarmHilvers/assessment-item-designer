"""Build the portable upload package and publish each manifest version once."""

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import urllib.error
import urllib.request
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_png(path, minimum):
    data = path.read_bytes()
    require(data.startswith(b'\x89PNG\r\n\x1a\n') and len(data) <= 5 * 1024 * 1024,
            f'Invalid or oversized PNG: {path}')
    offset, compressed, dimensions = 8, bytearray(), None
    while offset < len(data):
        length = struct.unpack('>I', data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        crc = data[offset + 8 + length:offset + 12 + length]
        require(len(crc) == 4 and struct.unpack('>I', crc)[0] == zlib.crc32(kind + payload),
                f'Broken PNG chunk: {path}')
        if kind == b'IHDR':
            dimensions = struct.unpack('>II', payload[:8])
        if kind == b'IDAT':
            compressed.extend(payload)
        offset += length + 12
        if kind == b'IEND':
            break
    require(dimensions is not None and dimensions[0] == dimensions[1]
            and minimum <= dimensions[0] <= 4096, f'Invalid icon dimensions: {path}')
    require(bool(compressed) and bool(zlib.decompress(compressed)), f'Broken PNG data: {path}')


def build_package(root, output):
    manifest = json.loads((root / 'plugin.json').read_text())
    name, version = manifest['name'], manifest['version']
    require(name == 'assessment-item-designer', 'Unexpected plugin identity')
    require(re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', version),
            'Version must be a stable semantic version')
    compatibility = json.loads((root / '.codex-plugin/plugin.json').read_text())
    ui = manifest['extensions']['com.openai']['interface']
    require(compatibility['name'] == name and compatibility['version'] == version
            and compatibility['interface'] == ui, 'Compatibility manifest is out of sync')
    for data in (manifest, compatibility):
        require(data.get('apps') is None
                and data.get('extensions', {}).get('com.openai', {}).get('apps') is None,
                'Public upload must not contain app bindings')
    require(not (root / '.app.json').exists() and not (root / 'mcp.json').exists(),
            'This release builder supports the skills-only package')
    for field, limit in [('displayName', 30), ('shortDescription', 30), ('longDescription', 4000)]:
        require(isinstance(ui[field], str) and 0 < len(ui[field]) <= limit,
                f'Invalid listing field: {field}')
    prompts = ui['defaultPrompt']
    prompts = [prompts] if isinstance(prompts, str) else prompts
    require(1 <= len(prompts) <= 3 and all(isinstance(p, str) and p.strip()
            and '\n' not in p and len(p) <= 128 for p in prompts), 'Invalid default prompts')
    require(len({' '.join(p.split()) for p in prompts}) == len(prompts), 'Duplicate prompts')

    paths = {'plugin.json', '.codex-plugin/plugin.json', 'LICENSE'}
    for field, minimum in [('logo', 256), ('composerIcon', 48)]:
        relative = Path(ui[field])
        require(not relative.is_absolute() and '..' not in relative.parts
                and relative.parts[0] == 'assets', 'Icon must be contained in assets/')
        path = root / relative
        require(path.is_file() and not path.is_symlink(), f'Missing icon: {relative}')
        validate_png(path, minimum)
        paths.add(relative.as_posix())
    skill = root / 'skills/assessment-item-designer'
    require((skill / 'SKILL.md').is_file(), 'Missing skill')
    for path in skill.rglob('*'):
        require(not path.is_symlink(), f'Symlink in skill: {path}')
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            paths.add(path.relative_to(root).as_posix())
    release = '.'.join(version.split('.')[:2])
    validator = skill / 'scripts/validate_audit.py'
    constants = {node.targets[0].id: ast.literal_eval(node.value)
                 for node in ast.parse(validator.read_text()).body
                 if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                 and node.targets[0].id in {'RELEASE', 'MANIFEST_VERSION'}}
    require(constants == {'RELEASE': release, 'MANIFEST_VERSION': version},
            'Audit validator version is out of sync')
    instructions = (skill / 'SKILL.md').read_text()
    require(f'Manifest version: **{version}**' in instructions
            and f'Release designation: **{release}**' in instructions,
            'Skill version is out of sync')
    for relative in sorted(paths):
        path = root / relative
        require(path.is_file() and not path.is_symlink(), f'Missing package file: {relative}')
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if not link.startswith(('https:', 'http:', '#', 'skill:')):
                    require((path.parent / link.split('#')[0]).exists(), f'Broken reference: {link}')

    output.mkdir(parents=True, exist_ok=True)
    archive = output / f'{name}-{version}-upload.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for relative in sorted(paths):
            # Stable timestamps let retries verify existing draft assets by digest.
            info = zipfile.ZipInfo(f'{name}/{relative}', (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, (root / relative).read_bytes())
    with zipfile.ZipFile(archive) as bundle:
        require(bundle.testzip() is None, 'ZIP integrity check failed')
        require(set(bundle.namelist()) == {f'{name}/{p}' for p in paths}, 'Incorrect ZIP inventory')
        for relative in paths:
            require(bundle.read(f'{name}/{relative}') == (root / relative).read_bytes(),
                    f'ZIP content mismatch: {relative}')
    return manifest, archive


def get_release(repository, tag):
    request = urllib.request.Request(
        f'https://api.github.com/repos/{repository}/releases/tags/{tag}',
        headers={'Authorization': f'Bearer {os.environ["GH_TOKEN"]}',
                 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def publish(root, manifest, archive):
    repository = os.environ['GITHUB_REPOSITORY']
    require(os.environ.get('GITHUB_REF') == 'refs/heads/main', 'Publishing is restricted to main')
    version = manifest['version']
    tag = f'v{version}'
    existing = get_release(repository, tag)
    if existing and not existing['draft']:
        print(f'Release {tag} already exists; left unchanged: {existing["html_url"]}')
        return 'existing'
    sha = os.environ['GITHUB_SHA']
    require(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip() == sha,
            'Checkout does not match the workflow commit')
    tag_commit = subprocess.run(['git', 'rev-parse', '--verify', f'refs/tags/{tag}^{{commit}}'],
                                cwd=root, text=True, capture_output=True)
    require(tag_commit.returncode != 0 or tag_commit.stdout.strip() == sha,
            f'Tag {tag} points at another commit; refusing to overwrite it')
    command = ['gh', 'release']
    if not existing:
        notes = archive.parent / 'release-notes.md'
        notes.write_text(manifest['extensions']['com.openai']['publication']['release_notes'] + '\n')
        subprocess.run(command + ['create', tag, str(archive), '--repo', repository,
                       '--target', sha, '--title', f'Assessment Item Designer {version}',
                       '--notes-file', str(notes), '--draft'], check=True, cwd=root)
    else:
        require(tag_commit.returncode == 0 or existing.get('target_commitish') == sha,
                'Existing draft targets another commit')
        assets = [asset for asset in existing['assets'] if asset['name'] == archive.name]
        if assets:
            digest = 'sha256:' + hashlib.sha256(archive.read_bytes()).hexdigest()
            require(len(assets) == 1 and assets[0].get('digest') == digest,
                    'Existing draft asset differs; refusing to overwrite it')
        else:
            subprocess.run(command + ['upload', tag, str(archive), '--repo', repository],
                           check=True, cwd=root)
    # Publish only after the complete, verified ZIP has been attached.
    subprocess.run(command + ['edit', tag, '--repo', repository, '--draft=false'], check=True, cwd=root)
    saved = get_release(repository, tag)
    require(saved and not saved['draft'] and any(a['name'] == archive.name for a in saved['assets']),
            'Published release or ZIP could not be verified')
    print(f'Published {saved["html_url"]}')
    return 'published'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    manifest, archive = build_package(ROOT, args.output)
    print(f'Verified upload ZIP: {archive}')
    if args.publish:
        status = publish(ROOT, manifest, archive)
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
                output.write(f'release_status={status}\n')


if __name__ == '__main__':
    main()
