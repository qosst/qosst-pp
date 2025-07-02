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
Module defining error reconciliation functions for Alice and Bob.
"""
import logging
from typing import Optional, List, Dict

import numpy as np

from qosst_core.control_protocol.sockets import QOSSTClient, QOSSTServer
from qosst_core.control_protocol.codes import QOSSTCodes

logger = logging.getLogger(__name__)

try:
    import information_reconciliation as ir
except ModuleNotFoundError:
    logger.warning(
        "information_reconciliation module is not present. IR cannot be performed."
    )


def reconcile_alice(
    socket: QOSSTServer,
    alice_symbols: np.ndarray,
    mdr_dimension: int,
    data: Optional[Dict],
) -> Optional[List[int]]:
    """Perform error reconciliation using IR_FOR_CVQKD.

    This function starts after receiving the EC_INITIALIZATION message from Bob.

    Ths function starts by getting the channel message, syndrome, normalization
    vector and SNR to perform the decoding. If the syndrome matches, the block is kept,
    and a CRC is computed. All the CRC are sent to Bob. Alice receives the final
    discard flags before returning the key.

    Args:
        socket (QOSSTServer): socket of the server of Alice.
        alice_symbols (np.ndarray): symbols of Alice, as an array of real numbers.
        mdr_dimension (int): dimension of the multidimensional reconciliation.
        data (Optional[Dict]): data of the received EC_INITIALIZATION message.

    Returns:
        Optional[List[int]]: reconciled key.
    """
    if alice_symbols[0].imag:
        logger.warning(
            "reconcile_alice takes as input a real array for Alice's symbols and alice_symbols[0] has non-zero imaginary part. This is likely to fail."
        )
    if (
        not data
        or not "channel_message" in data
        or not "syndrome" in data
        or not "normalization_vector" in data
        or not "signal_to_noise_ratio" in data
    ):
        logger.error(
            "channel_message or syndrome or normalization_vector or signal_to_noise_ratio is missing from EC_INITIALIZATION."
        )
        socket.send(
            QOSSTCodes.INVALID_CONTENT,
            {
                "error_message": "channel_message or syndrome or normalization_vector or signal_to_noise_ratio parameter was not present in the content."
            },
        )
        return None

    channel_message = data["channel_message"]
    syndrome = data["syndrome"]
    normalization_vector = data["normalization_vector"]
    signal_to_noise_ratio = data["signal_to_noise_ratio"]

    crc_alice, discard_flags, decoded_frames = ir.reconcile_Alice(
        alice_states=alice_symbols,
        classical_channel_message=channel_message,
        syndrome=syndrome,
        normalization_vector=normalization_vector,
        SNR=signal_to_noise_ratio,
        MDR_dim=mdr_dimension,
    )

    if not crc_alice or not discard_flags or not decoded_frames:
        logger.error("Error happened on error correction at Alice's side.")
        socket.send(QOSSTCodes.EC_ERROR)
        return None

    socket.send(
        QOSSTCodes.EC_VERIFICATION,
        {"crc_alice": crc_alice, "discard_flags": discard_flags},
    )

    logger.info("Discard flags : %s", str(discard_flags))

    code, data = socket.recv()

    if code != QOSSTCodes.EC_DISCARD_FLAGS:
        logger.error("Unexpected command %s.", str(code))
        socket.send(QOSSTCodes.UNEXPECTED_COMMAND)
        return None

    if not data or not "final_discard_flags" in data:
        logger.error("final_discard_flagsis missing from EC_INITIALIZATION.")
        socket.send(
            QOSSTCodes.INVALID_CONTENT,
            {
                "error_message": "final_discard_flags parameter was not present in the content."
            },
        )
        return None

    final_discard_flags = data["final_discard_flags"]
    logger.info("Final discard flags : %s", str(final_discard_flags))

    alice_final_keys = [
        frame for frame, flag in zip(decoded_frames, final_discard_flags) if flag == 0
    ]

    socket.send(QOSSTCodes.EC_FINISHED)

    # Make the array flat (instead of list of blocks)
    reconciled_key = list(np.ravel(alice_final_keys))
    logger.info("Reconciled key has length %i", len(reconciled_key))
    return reconciled_key


# pylint: disable=too-many-locals
def reconcile_bob(
    socket: QOSSTClient,
    bob_symbols: np.ndarray,
    beta: float,
    signal_to_noise_ratio: float,
    mdr_dimension: int,
) -> Optional[List[int]]:
    """Perform the reconciliation at Bob side.

    Start by computing channel messages, syndrome, normalization vector
    and raw key and send the EC_INITIALIZATION message with the channel
    messages, syndrome, normalization vector and SNR. Then, it waits
    for the discard flags and CRC from Alice, before discarding and computing
    the CRC and kept frames, to send the final discard flags to Alice.

    Args:
        socket (QOSSTClient): client socket of Bob.
        bob_symbols (np.ndarray): bob symbols, as an array of real numbers.
        beta (float): reconciliation effiency, from which the rate is derived.
        signal_to_noise_ratio (float): signal to noise ratio of the quantum data.
        mdr_dimension (int): dimension of the multi-dimensional scheme.

    Returns:
        Optional[List[int]]: reconciled key.
    """

    if bob_symbols[0].imag:
        logger.warning(
            "reconcile_bob takes as input a real array for Bob's symbols and bob_symbols[0] has non-zero imaginary part. This is likely to fail."
        )

    (channel_message, syndrome, normalization_vector, raw_key) = ir.reconcile_Bob(
        bob_states=bob_symbols,
        beta=beta,
        SNR=signal_to_noise_ratio,
        MDR_dim=mdr_dimension,
    )

    if not channel_message or not syndrome or not normalization_vector or not raw_key:
        logger.error("Error happened on error correction at Bob's side.")
        return None

    # Sent to Alice and wait for CRC_Alice and discard_flag to Bob
    code, data = socket.request(
        QOSSTCodes.EC_INITIALIZATION,
        {
            "channel_message": channel_message,
            "syndrome": syndrome,
            "normalization_vector": normalization_vector,
            "signal_to_noise_ratio": signal_to_noise_ratio,
        },
    )

    if code != QOSSTCodes.EC_VERIFICATION:
        logger.error("Error happened during Alice's error reconciliation.")
        return None

    if not data or not "crc_alice" in data or not "discard_flags" in data:
        logger.error("crc_alice or discard_flags is missing from EC_VERIFICATION.")
        return None

    crc_alice = data["crc_alice"]
    alice_discard_flags = data["discard_flags"]

    logger.info("Alice discard flags %s", str(alice_discard_flags))

    (final_discard_flags, bob_final_keys) = ir.CRC_check_Bob(
        raw_keys=raw_key, CRC_Alice=crc_alice, discard_flag=alice_discard_flags
    )
    code, data = socket.request(
        QOSSTCodes.EC_DISCARD_FLAGS, {"final_discard_flags": final_discard_flags}
    )

    logger.info("Final discard flags %s", str(final_discard_flags))

    # Make the array flat (instead of list of blocks)
    reconciled_key = list(np.ravel(bob_final_keys))
    logger.info("Reconciled key has length %i", len(reconciled_key))

    return reconciled_key
