# qosst-pp - Post processing module of the Quantum Open Software for Secure Transmissions.
# Copyright (C) 2021-2025 Yoann Piétri

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
This file will contain the code for script interactions.

It will call commands for the submodules.
"""
import logging
import argparse

from qosst_core.logging import create_loggers

from qosst_pp import __version__
from qosst_pp.install import (
    install_ir_for_cvqkd,
    install_cryptomite,
    uninstall_ir_for_cvqkd,
    uninstall_cryptomite,
)

logger = logging.getLogger(__name__)


def _create_main_parser() -> argparse.ArgumentParser:
    """
    Create the main parser.

    Commands:
        install

    Returns:
        argparse.ArgumentParser: the main parser.
    """
    parser = argparse.ArgumentParser(prog="qosst-pp")

    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Level of verbosity. If none, only critical errors will be prompted. -v will add warnings and errors, -vv will add info and -vvv will print all debug logs.",
    )

    subparsers = parser.add_subparsers()

    install_parser = subparsers.add_parser(
        "install", help="Install non-pypi dependenies for qosst-pp"
    )
    install_parser.set_defaults(func=install)
    install_parser.add_argument(
        "package",
        choices=["IR_for_CVQKD", "cryptomite"],
        help="Name of the package to install",
    )

    uninstall_parser = subparsers.add_parser(
        "uninstall", help="Uninstall non-pypi dependenies for qosst-pp"
    )
    uninstall_parser.set_defaults(func=uninstall)
    uninstall_parser.add_argument(
        "package",
        choices=["IR_for_CVQKD", "cryptomite"],
        help="Name of the package to uninstall",
    )

    return parser


# pylint: disable=too-many-locals
def main():
    """
    This is the actual entrypoint.

    It will construct the parser and subparsers for the different command.
    """
    parser = _create_main_parser()

    args = parser.parse_args()
    create_loggers(args.verbose, None)

    if hasattr(args, "func"):
        args.func(args)
    else:
        print("No command specified. Run with -h|--help to see the possible commands.")


def install(args: argparse.Namespace) -> bool:
    """
    Install command.

    Args:
        args (argparse.Namespace): the args passed to the command line.

    Returns:
        bool: True if the package is successfully installed, False otherwise.
    """
    logger.warning("install script is an experimental feature")
    if args.package == "IR_for_CVQKD":
        return install_ir_for_cvqkd()
    if args.package == "cryptomite":
        return install_cryptomite()
    return False


def uninstall(args: argparse.Namespace) -> bool:
    """
    Uninstall command.

    Args:
        args (argparse.Namespace): the args passed to the command line.

    Returns:
        bool: True if the package is successfully uninstalled, False otherwise.
    """
    if args.package == "IR_for_CVQKD":
        return uninstall_ir_for_cvqkd()
    if args.package == "cryptomite":
        return uninstall_cryptomite()
    return False


if __name__ == "__main__":
    main()
