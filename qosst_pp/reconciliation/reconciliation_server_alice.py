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
Reconciliation server for Alice.
"""


import logging
import argparse

import zmq
import numpy as np

from qosst_core.control_protocol.sockets import QOSSTServer
from qosst_core.control_protocol.codes import QOSSTCodes
from qosst_core.logging import create_loggers

from qosst_pp import __version__
from qosst_pp.reconciliation.reconciliation import reconcile_alice

logger = logging.getLogger(__name__)


def reconciliation_server_alice(
    listening_host: str, listening_port: int, internal_endpoint: str
):
    """Start reconciliation server for Alice.

    Args:
        listening_host (str): address to bind to for QOSST socket.
        listening_port (int): port to bind to for QOSST socket.
        internal_endpoint (str): endpoint for the ZMQ socket.
    """
    zmq_context = zmq.Context()
    while True:
        try:
            logger.info("Starting Bob reconciliation server")

            # Create zmq listener to receive the data
            logger.info("Creating ZMQ socket at %s", internal_endpoint)
            zmq_socket = zmq_context.socket(zmq.REP)
            zmq_socket.bind(internal_endpoint)

            # Receive the data from Alice
            logger.info("Waiting for a request from Alice.")
            data = zmq_socket.recv_json()

            logger.info("Request received.")
            alice_symbols = np.array(data["alice_symbols"])
            mdr_dimension = data["mdr_dimension"]

            # Create QOSST socket
            socket = QOSSTServer(listening_host, listening_port)

            logger.info("Binding to %s:%s", listening_host, listening_port)
            socket.open()

            logger.info("Waiting for a client to connect.")
            socket.connect()

            code, data = socket.recv()

            assert code == QOSSTCodes.EC_INITIALIZATION

            key = reconcile_alice(socket, alice_symbols, mdr_dimension, data)

            logger.info("Reconciliation finished, returning keys.")
            # Return key to the application
            zmq_socket.send_json({"key": key})

            logger.info("Closing sockets.")
            socket.close()
            zmq_socket.close()
        except KeyboardInterrupt:
            logger.info("Stopping server.")
            zmq_context.term()
            return


def _create_parser() -> argparse.ArgumentParser:
    """Create the parser for qosst-pp-server-alice.

    Returns:
        argparse.ArgumentParser: the argument parser.
    """
    parser = argparse.ArgumentParser(prog="qosst-pp-server-alice")

    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Level of verbosity. If none, only critical errors will be prompted. -v will add warnings and errors, -vv will add info and -vvv will print all debug logs.",
    )

    parser.add_argument("remote_host", help="Address of the remote host to bind to.")
    parser.add_argument(
        "remote_port", help="Port of the remote host to bind to.", type=int
    )
    parser.add_argument("endpoint", help="Endpoint to bind the server to.")

    return parser


def main():
    """
    Main entrypoint of qosst-pp-server-alice.
    """
    parser = _create_parser()

    args = parser.parse_args()

    create_loggers(args.verbose, None)

    reconciliation_server_alice(args.remote_host, args.remote_port, args.endpoint)


if __name__ == "__main__":
    main()
