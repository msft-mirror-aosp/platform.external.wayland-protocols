#!/usr/bin/python3
# Copyright 2024 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import datetime
import logging
import pathlib
import re
import shutil
import subprocess
import sys

DESCRIPTION = (
    'Helper script for importing a snapshot from upstream Wayland protocol '
    'sources.')

INTENDED_USAGE = ('''
Intended Usage:
    # Update the freedesktop.org subdirectory to version 1.32
    # Check https://gitlab.freedesktop.org/wayland/wayland-protocols/-/tags
    # for valid version tags.
    ./import_snapshot.py freedesktop.org 1.32

    # Update the chromium.org subdirectory to the latest
    ./import_snapshot.py chromium.org main
''')


class GitRepo:
    """Issues git commands against a local checkout located at some path."""

    def __init__(self, base: pathlib.PurePath):
        logging.debug("GitRepo base %s", base)
        self._base = base

    @property
    def base(self) -> pathlib.PurePath:
        """Gets the base path used the repo."""
        return self._base

    def _git(self,
             cmd: list[str],
             capture_output: bool = True,
             check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(['git', '-C', self._base] + cmd,
                              capture_output=capture_output,
                              check=check,
                              text=True)

    def get_hash_for_version(self, version) -> str:
        """Gets the hash associated with a |version| tag or branch."""
        logging.debug("GitRepo.get_hash_for_version version %s", version)
        return self._git(['show-ref', '--hash',
                          version]).stdout.splitlines()[0].strip()

    def git_ref_name_for_version(self, version) -> str | None:
        """Gets the named ref corresponding to |version|, if one exists."""
        logging.debug("GitRepo.get_ref_name_for_version version %s", version)
        ref = self._git(['describe', '--all', '--exact-match', version],
                        check=False).stdout.splitlines()[0].strip()
        if ref.startswith('tags/'):
            return ref.removeprefix('tags/')
        if ref.startswith('heads/'):
            return ref.removeprefix('heads/')
        return None

    def get_files(self, version: str,
                  paths: list[pathlib.PurePath]) -> list[pathlib.Path]:
        """Gets the list of files under |paths| that are part of the Git tree at |version|."""
        logging.debug("GitRepo.get_files version %s paths %s", version, paths)
        stdout = self._git(
            ['ls-tree', '-r', '--name-only', f'{version}^{{tree}}'] +
            paths).stdout
        return list(pathlib.PurePath(path) for path in stdout.splitlines())

    def assert_no_uncommitted_changes(self) -> None:
        """Asserts that the repo has no uncommited changes."""
        r = self._git(['diff-files', '--quiet', '--ignore-submodules'],
                      check=False)
        if r.returncode:
            sys.exit('Error: Your tree is dirty')

        r = self._git([
            'diff-index', '--quiet', '--ignore-submodules', '--cached', 'HEAD'
        ],
                      check=False)
        if r.returncode:
            sys.exit('Error: You have staged changes')

    def sparse_depth1_clone(self,
                            url: str,
                            version: str | None,
                            paths: list[str],
                            force_clean: bool = True) -> None:
        """Performs a sparse clone with depth=1 of a repo.

        A sparse clone limits the clone to a particular set of files, and not
        all the files available in the repo.

        A depth=1 clone fetches only the most recent version of each file
        cloned, and not the entire history.

        Together that makes the checkout be faster and take up less space on
        disk, which is important for large repositories like the Chromium
        source tree.

        |url| gives the url to the remote repository to clone.

        |version| gives the version to clone. If not specified, 'HEAD' is assumed.

        Paths in |paths| are included in the sparse checkout, which also means
        all files in the parents directories leading up to those directories are
        included. if |paths| is an empty list, all files at the root of the
        repository will be included.

        |force_clean| ensures any existing checkout at |base| is removed.
        Setting this to False speeds up testing changes to the script when
        syncing a particular version, as it will only be cloned the first
        time.
        """
        logging.debug(
            "GitRepo.sparse_depth1_clone url %s version %s paths %s force_clean %s",
            url, version, paths, force_clean)
        self._base.parent.mkdir(parents=True, exist_ok=True)
        if force_clean and self._base.exists():
            shutil.rmtree(self._base)

        if not self._base.exists():
            cmd = ['git', 'clone', '--filter=blob:none', '--depth=1']
            if paths:
                cmd.extend(['--sparse'])
            if version is not None and version != 'HEAD':
                cmd.extend(['-b', version])
            cmd.extend([url, self._base])

            subprocess.run(cmd, capture_output=False, check=True, text=True)

            if paths:
                self._git(['sparse-checkout', 'add'] + paths)

    def add(self, path: pathlib.Path) -> None:
        """Stages a local file |path| in the index."""
        logging.debug("GitRepo.add path %s", path)
        self._git(['add', path])

    def commit(self,
               message: str,
               allow_empty: bool = False,
               auto_add: bool = True) -> None:
        """Commits stages changed using |message|.

        If |allow_empty| is true, an empty commit is allowed.
        If |auto_add| is true, changed files are added automatically.
        """
        logging.debug("GitRepo.commit message %s allow_empty %s auto_add %s",
                      message, allow_empty, auto_add)
        cmd = ['commit', '-m', message]
        if allow_empty:
            cmd.extend(['--allow-empty'])
        if auto_add:
            cmd.extend(['-a'])

        self._git(cmd, capture_output=False)


class AndroidMetadata:
    """Minimal set of functions for reading and updating METADATA files.

    Officially these files are meant to be read and written using code
    generated from
    //build/soong/compliance/project_metadata_proto/project_metadata.proto,
    but using it would require adding a dependency on Python protocol buffer
    libraries as well as the generated code for the .proto file.

    Instead we use the Python regex library module to parse and rewrite the
    metadata, as we don't need to do anything really complicated.
    """

    def __init__(self, metadata_path: pathlib.Path):
        assert metadata_path.exists()
        self._metadata_path: pathlib.Path = metadata_path
        self._content: str | None = None
        self._url: str | None = None
        self._paths: list[pathlib.PurePath] | None = None

    def _read_content(self) -> None:
        if self._content is None:
            with open(self._metadata_path, 'rt') as metadata_file:
                self._content = metadata_file.read()

    def _write_content(self) -> None:
        if self._content is not None:
            with open(self._metadata_path, 'wt') as metadata_file:
                metadata_file.write(self._content)

    def _read_raw_git_urls(self) -> None:
        if self._url is None:
            self._read_content()

            paths = []
            URL_PATTERN = r'url\s*{\s*type:\s*GIT\s*value:\s*"([^"]*)"\s*}'
            for url in re.findall(URL_PATTERN, self._content):
                base_url = url
                path = None

                if '/-/tree/' in url:
                    base_url, path = url.split('/-/tree/')
                    _, path = path.split('/', 1)
                elif '/+/' in url:
                    base_url, path = url.split('/+/')
                    _, path = path.split('/', 1)

                if self._url and self._url != base_url:
                    sys.exit(
                        f'Error: Inconsistent git URLs in {self._metadata_path} ({self._url} vs {base_url})'
                    )

                self._url = base_url
                if path:
                    paths.append(path)

            self._paths = tuple(paths)

    @property
    def current_version(self) -> str:
        """Obtains the current version according to the metadata."""
        self._read_content()

        match = re.search(r'version: "([^"]*)"', self._content)
        if not match:
            sys.exit(
                f'Error: Unable to determine current version from {self._metadata_path}'
            )
        return match.group(1)

    @property
    def git_url(self) -> str:
        """Obtains the git URL to use from the metadata."""
        self._read_raw_git_urls()
        return self._url

    @property
    def git_paths(self) -> list[pathlib.PurePath]:
        """Obtains the child paths to sync from the metadata.

        This can be an empty list if the entire repo should be synced.
        """
        self._read_raw_git_urls()
        return list(self._paths)

    def update_version_and_import_date(self, version: str) -> None:
        """Updates the version and import date in the metadata.

        |version| gives the version string to write.
        The import date is set to the current date.
        """
        self._read_content()

        now = datetime.datetime.now()
        self._content = re.sub(r'version: "[^"]*"', f'version: "{version}"',
                               self._content)
        self._content = re.sub(
            r'last_upgrade_date {[^}]*}',
            (f'last_upgrade_date {{ year: {now.year} month: {now.month} '
             f'day: {now.day} }}'), self._content)

        self._write_content()


def must_ignore(path: pathlib.PurePath) -> bool:
    """Checks if |path| should be ignored and not imported, as doing so might conflict with Android metadata.."""
    IGNORE_PATTERNS: tuple[str] = (
        'METADATA',
        'MODULE_LICENSE_*',
        '**/OWNERS',
        '**/Android.bp',
    )
    ignore = any(path.match(pattern) for pattern in IGNORE_PATTERNS)
    if ignore:
        print('Ignoring source {path}')
    return ignore


def main():
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=INTENDED_USAGE,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('group',
                        default=None,
                        help='The subdirectory (group) to update')

    parser.add_argument(
        'version',
        nargs='?',
        default='HEAD',
        help='The official version to import. Uses HEAD by default.')

    parser.add_argument('--loglevel',
                        default='INFO',
                        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR',
                                 'CRITICAL'),
                        help='Logging level.')

    parser.add_argument('--no-force-clean',
                        dest='force_clean',
                        default=True,
                        action='store_false',
                        help='Disables clean fetches of upstream code')

    parser.add_argument(
        '--no-remove-old-files',
        dest='remove_old_files',
        default=True,
        action='store_false',
        help=
        'Disables syncing the previous version to determine what files to remove'
    )

    args: argparse.ArgumentParser = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.loglevel))

    base = pathlib.Path(sys.argv[0]).parent.resolve().absolute()
    assert base.exists()

    print(
        f'Importing {args.group} Wayland protocols at {args.version} to {args.group}'
    )

    target_git = GitRepo(base)
    target_git.assert_no_uncommitted_changes()
    target_group_path = base / args.group

    meta = AndroidMetadata(target_group_path / 'METADATA')

    print(f'Cloning {meta.git_url} [sparse/limited] at {args.version}')
    import_new_git = GitRepo(base / '.import' / args.group / (args.version))
    import_new_git.sparse_depth1_clone(meta.git_url,
                                       args.version,
                                       meta.git_paths,
                                       force_clean=args.force_clean)
    import_new_hash = import_new_git.get_hash_for_version(args.version)
    import_new_ref_name = import_new_git.git_ref_name_for_version(args.version)
    print(f'Synced "{import_new_hash} ({import_new_ref_name})"')
    import_new_files = import_new_git.get_files(import_new_hash,
                                                meta.git_paths)
    if args.remove_old_files:
        print(
            f'Cloning {meta.git_url} [sparse/limited] at prior {meta.current_version}'
        )
        import_old_git = GitRepo(base / '.import' / args.group /
                                 meta.current_version)
        import_old_git.sparse_depth1_clone(meta.git_url,
                                           meta.current_version,
                                           meta.git_paths,
                                           force_clean=args.force_clean)
        import_old_hash = import_old_git.get_hash_for_version(
            meta.current_version)
        print(f'Synced "{import_old_hash}"')
        import_old_files = import_old_git.get_files(import_old_hash,
                                                    meta.git_paths)

        files_to_remove = set(import_old_files).difference(import_new_files)
        for path in files_to_remove:
            if must_ignore(path):
                continue
            old: pathlib.Path = target_group_path / path
            logging.debug("removing old path %s", old)
            old.unlink(missing_ok=True)

    for path in import_new_files:
        if must_ignore(path):
            continue
        src: pathlib.Path = import_new_git.base / path
        dst: pathlib.Path = target_group_path / path
        logging.debug("copying %s to %s", src, dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        target_git.add(target_group_path / path)

    meta.update_version_and_import_date(import_new_ref_name or import_new_hash)
    target_git.add(target_group_path / 'METADATA')

    message = f'''
Update to {args.group} protocols {import_new_ref_name or import_new_hash}

This imports {import_new_hash} from the upstream repository.

Test: Builds
'''.lstrip()
    target_git.commit(message, allow_empty=True)


if __name__ == '__main__':
    main()
