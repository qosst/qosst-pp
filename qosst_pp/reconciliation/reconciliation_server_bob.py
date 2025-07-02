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
Reconciliation server for Bob.
"""

import logging
import argparse
from typing import List

import zmq
import numpy as np

from qosst_core.control_protocol.sockets import QOSSTClient
from qosst_core.logging import create_loggers

from qosst_pp import __version__
from qosst_pp.reconciliation.reconciliation import reconcile_bob

logger = logging.getLogger(__name__)


def reconciliation_server_bob(
    remote_host: str, remote_port: int, internal_endpoint: str
):
    """Start reconciliation server for Alice.

    Args:
        remote_host (str): address to connect to for QOSST socket.
        remote_port (int): port to connect to for QOSST socket.
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

            # Receive the data from Bob
            logger.info("Waiting for a request from Bob.")
            data = zmq_socket.recv_json()

            logger.info("Request received.")

            bob_symbols = np.array(data["bob_symbols"])
            beta = data["beta"]
            signal_to_noise_ratio = data["signal_to_noise_ratio"]
            mdr_dimension = data["mdr_dimension"]

            # Create QOSST socket
            logger.info("Starting QOSST socket.")
            socket = QOSSTClient(remote_host, remote_port)
            socket.open()

            logger.info("Connecting to %s:%s", remote_host, remote_port)
            socket.connect()

            logger.info("Starting reconciliation.")
            key = reconcile_bob(
                socket, bob_symbols, beta, signal_to_noise_ratio, mdr_dimension
            )

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
    parser = argparse.ArgumentParser(prog="qosst-pp-server-bob")

    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Level of verbosity. If none, only critical errors will be prompted. -v will add warnings and errors, -vv will add info and -vvv will print all debug logs.",
    )

    parser.add_argument("remote_host", help="Address of the remote host to connect to.")
    parser.add_argument(
        "remote_port", help="Port of the remote host to connect to.", type=int
    )
    parser.add_argument("endpoint", help="Endpoint to bind the server to.")

    return parser


def main():
    """
    Main entrypoint of qosst-pp-server-bob.
    """
    parser = _create_parser()

    args = parser.parse_args()

    create_loggers(args.verbose, None)

    reconciliation_server_bob(args.remote_host, args.remote_port, args.endpoint)


if __name__ == "__main__":
    main()
