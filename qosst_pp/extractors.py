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
Module defining randomness extactors for privacy amplification.
"""

import logging
from typing import List, Optional, Tuple

from cryptomite.toeplitz import Toeplitz

from qosst_core.extractors import RandomnessExtractor

logger = logging.getLogger(__name__)


class ToeplitzExtractor(RandomnessExtractor):
    """
    Randomness extractor using the Toeplitz extractor from cryptomite.
    """

    @property
    def seed_size(self) -> int:
        """
        Seed size for (n,m) Toeplitz extractor is
        n*m-1.

        Returns:
            int: the seed size
        """
        return self.reconciled_key_size + self.final_key_size - 1

    def _extract(
        self, reconciled_key: List[int], seed: List[int]
    ) -> Tuple[Optional[List[int]], Optional[List[int]]]:
        logger.info(
            "Extracting key with Toeplitz extractor. Reconciled key length %i and final key length %i.",
            self.reconciled_key_size,
            self.final_key_size,
        )
        extractor = Toeplitz(self.reconciled_key_size, self.final_key_size)
        return extractor.extract(reconciled_key, seed), seed
