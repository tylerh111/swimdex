import argparse
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence, TypeVar

import nox
import setuptools_scm

nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["build"]

DOCS = Path("docs")
SITE = Path("site")

REQUIREMENTS = {
    "build": "requirements/build.txt",
}

F = TypeVar("F", bound=Callable[..., Any])

def _get_version():
    return setuptools_scm.get_version(version_scheme="no-guess-dev")

def _add_args_if(
    test: bool,
    *args: str,
):
    """Usage: `*_add_args_if(...)`"""
    return args if test else ()


def _parse_args(
    session: nox.Session,
    args: Sequence[str],
    name: str,
    *options: Mapping[str, Any],
    description: str = None,
    epilog: str = None,
    command: str = None,
    add_ellipse_to_usage: bool = True,
):
    """Usage: _parser_args(session.posargs, <name>, <argument>, ...)"""

    class EllipsisHelpFormatter(argparse.RawTextHelpFormatter):
        @staticmethod
        def _add_ellipse_to_usage(usage: str):
            if not add_ellipse_to_usage:
                return usage
            has_newline = usage.endswith("\n")
            usage = usage.rstrip("\n")
            usage = (usage + " ...") if not usage.endswith("...") else usage
            usage = (usage + "\n") if has_newline else usage
            return usage

        def format_help(self):
            help = super().format_help()
            if help:
                usage, *help = help.splitlines(keepends=True)
                usage = self._add_ellipse_to_usage(usage)
                help = "".join((usage, *help))
            return help

    if not command:
        command = "underlying command(s)"

    if not epilog:
        epilog = f"remaining:\n  passed to {command}"

    parser = argparse.ArgumentParser(
        prog=name,
        description=description,
        formatter_class=EllipsisHelpFormatter,
        epilog=epilog,
    )
    for option in options:
        names = option.pop("args")
        names = [names] if isinstance(names, str) else names
        parser.add_argument(*names, **option)

    try:
        return parser.parse_known_intermixed_args(args)
    except SystemExit:
        session.error()


# =============================================================================
#  sessions
# =============================================================================


@nox.session(name="version")
def version(session: nox.Session):
    """Show version"""
    version = _get_version()
    session.log(f"swimdex {version}")


@nox.session(name="bump")
def bump(session: nox.Session):
    """Bump version"""
    _, remaining = _parse_args(
        session,
        session.posargs,
        "nox -s bump",
        command="`bumpver update`",
    )

    if all(arg not in ("--major", "--minor", "--patch", "-m", "-p") for arg in remaining):
        remaining.append("--minor")

    def bumpver_update_command():
        return [
            "bumpver",
            "update",
        ]

    session.install("bumpver")
    session.log("# Bumping version")
    session.run(*bumpver_update_command(), *remaining)


@nox.session(name="build")
def build(session: nox.Session):
    """Build site"""
    _, remaining = _parse_args(
        session,
        session.posargs,
        "nox -s build",
        command="`mkdocs build`",
    )

    docs = DOCS
    site = SITE
    version = _get_version()

    def mkdocs_build_command():
        return [
            "mkdocs",
            "build",
            "-d", site,
        ]

    session.install("-r", REQUIREMENTS["build"])
    session.log("# Building documentation")
    session.run(*mkdocs_build_command(), *remaining)

    with (
        open(docs / "overrides" / "version.html", mode="w") as f_docs,
        open(site / "overrides" / "version.html", mode="w") as f_site,
    ):
        f_site.write(version)
        f_docs.write(version)


@nox.session(name="release")
def release(session: nox.Session):
    """Deploy site"""
    _, remaining = _parse_args(
        session,
        session.posargs,
        "nox -s release",
        command="`mkdocs gh-deploy`",
    )

    version = _get_version()

    def mkdocs_deploy_command():
        return [
            "mkdocs",
            "gh-deploy",
        ]

    session.install("-r", REQUIREMENTS["build"])
    session.log(f"# Releasing version: {version}")
    session.run(*mkdocs_deploy_command(), *remaining)
