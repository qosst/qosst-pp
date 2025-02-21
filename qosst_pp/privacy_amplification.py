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
Module defining privacy amplification functions for Alice and Bob.
"""

import logging
from typing import List, Type, Optional, Dict

from qosst_core.control_protocol.sockets import QOSSTClient, QOSSTServer
from qosst_core.control_protocol.codes import QOSSTCodes
from qosst_core.extractors import RandomnessExtractor

logger = logging.getLogger(__name__)


def privacy_amplification_alice(
    socket: QOSSTServer,
    reconciled_key: List[int],
    extractor_class: Type[RandomnessExtractor],
    data: Optional[Dict],
) -> Optional[List[int]]:
    """
    Perform Alice privacy amplification.

    Function called after a PA request. Get seed from PA request
    and used the selected extractor to get the final key.

    Errors happen if the seed is not of the appropriate length or if
    the seed is not in the data of the message.

    Args:
        socket (QOSSTServer): the server socket of Alice.
        reconciled_key (List[int]): the reconciled key.
        secret_key_ratio (float): the secret key ratio in bits/symbol.
        extractor_class (Type[RandomnessExtractor]): the extractor class to use.
        data (Optional[Dict]): data of the received message of PA request.

    Returns:
        Optional[List[int]]: the final key of length int(len(reconciled_key)*secret_key_ratio)
    """
    if not data or not "seed" in data or not "secret_key_ratio" in data:
        logger.error("seed or secret_key_ratio is missing from PA_REQUEST.")
        socket.send(
            QOSSTCodes.INVALID_CONTENT,
            {
                "error_message": "Seed or secret_key_ratio parameter was not present in the content."
            },
        )
        return None

    seed = data["seed"]
    secret_key_ratio = data["secret_key_ratio"]

    logger.info("Using extractor %s", str(extractor_class))
    final_key_size = int(len(reconciled_key) * secret_key_ratio)

    extractor = extractor_class(len(reconciled_key), final_key_size)

    final_key, _ = extractor.extract(reconciled_key, seed)

    if final_key is not None:
        logger.info(
            "Successful privacy amplification. %i secret key bits obtained.",
            len(final_key),
        )
        socket.send(QOSSTCodes.PA_SUCCESS)
    else:
        logger.error("An error happened during extraction.")
        socket.send(
            QOSSTCodes.PA_ERROR,
            data={"error_message": "An error happened during extraction."},
        )

    return final_key


def privacy_amplification_bob(
    socket: QOSSTClient,
    reconciled_key: List[int],
    secret_key_ratio: float,
    extractor_class: Type[RandomnessExtractor],
) -> Optional[List[int]]:
    """
    Perform Bob privacy amplification.

    Start by extracting a key and getting the seed. Send the
    seed to Alice.

    Args:
        socket (QOSSTClient): client socket of Bob.
        reconciled_key (List[int]): reconciled key.
        secret_key_ratio (float): secret key ratio in bits/symbol.
        extractor_class (Type[RandomnessExtractor]): the extractor to use.

    Returns:
        Optional[List[int]]: the final key of length int(len(reconciled_key)*secret_key_ratio).
    """
    logger.info("Starting Bob privacy amplfication.")

    logger.info("Using extractor %s", str(extractor_class))

    final_key_size = int(secret_key_ratio * len(reconciled_key))
    extractor = extractor_class(len(reconciled_key), final_key_size)

    final_key, seed = extractor.extract(reconciled_key)

    if final_key is None:
        logger.error("An error happened during extraction.")
        return None

    code, _ = socket.request(
        QOSSTCodes.PA_REQUEST, {"seed": seed, "secret_key_ratio": secret_key_ratio}
    )

    if code == QOSSTCodes.PA_SUCCESS:
        logger.info(
            "Successful privacy amplification. %i secret key bits obtained.",
            len(final_key),
        )
        return final_key

    logger.error("Privacy amplification error received by Alice.")
    return None
