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
This module contains function to install non-pypi dependencies.
"""
import os
import site
import shutil
import subprocess
import logging
import tempfile
import glob
from importlib.util import find_spec

logger = logging.getLogger(__name__)

# Define constants
IR_REPO = "https://github.com/erdemeray/IR_for_CVQKD"
IR_COMMIT = "686d48e88d08f31110963d0d21537a9efef12d7f"
IR_COMMENTING_START = 29
IR_COMMENTING_END = 34
IR_PYTHON_REQUIREMENT_LINE = 44
IR_PYTHON_REQUIREMENT = (
    "find_package(Python REQUIRED COMPONENTS Interpreter Development)\n"
)

CM_REPO = "https://github.com/CQCL/cryptomite"


def install_ir_for_cvqkd() -> bool:
    """
    Install IR_for_CVQKD from https://github.com/erdemeray/IR_for_CVQKD

    Returns:
        bool: True in case of successful installation, False otherwise.
    """

    logger.info("Creating temporary directory")
    os.mkdir("deps")
    deps = "deps"
    logger.debug("Created directory %s", str(deps))

    os.chdir(deps)

    logger.info("Cloning IR_for_CVQKD")

    subprocess.run(["git", "clone", IR_REPO], check=True)

    os.chdir("IR_for_CVQKD")

    logger.info("Checking out to QOSST branch")
    subprocess.run(["git", "checkout", "QOSST"], capture_output=True, check=True)

    ret = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, check=True)
    last_commit_id = ret.stdout.decode("utf-8").replace("\n", "")

    if last_commit_id != IR_COMMIT:
        logger.warning(
            "Current commit %s is different from script target commit %s. Successful operation is not expected.",
            last_commit_id,
            IR_COMMIT,
        )

    os.chdir("IR_lib")

    logger.info("Commenting conda lines on CMakeLists.txt")

    with open("CMakeLists.txt", "r", encoding="utf-8") as file:
        data = file.readlines()
        for line_number in range(IR_COMMENTING_START, IR_COMMENTING_END + 1):
            initial = data[line_number - 1]
            data[line_number - 1] = "#" + data[line_number - 1]
            logger.debug(
                "Line %s at line no %i replaced with %s",
                initial.replace("\n", ""),
                line_number,
                data[line_number - 1].replace("\n", ""),
            )

    logger.info("Changing python requirement in CMakeLists.txt")

    initial = data[IR_PYTHON_REQUIREMENT_LINE - 1]
    data[IR_PYTHON_REQUIREMENT_LINE - 1] = IR_PYTHON_REQUIREMENT
    logger.debug(
        "Line %s at line no %i replaced with %s",
        initial.replace("\n", ""),
        IR_PYTHON_REQUIREMENT_LINE,
        data[IR_PYTHON_REQUIREMENT_LINE - 1].replace("\n", ""),
    )

    with open("CMakeLists.txt", "w", encoding="utf-8") as file:
        file.writelines(data)

    logger.info("Generating makefile")

    os.mkdir("build")
    os.chdir("build")

    subprocess.run(
        [
            "cmake",
            "..",
        ],
        check=True,
    )

    logger.info("Building package")

    subprocess.run(
        [
            "make",
        ],
        check=True,
    )

    logger.info("Copying shared library into python lib")

    for so_file in glob.glob("*.so"):
        dest = site.getsitepackages()[0]
        logger.debug("Copying %s to %s", so_file, dest)
        shutil.copy(str(so_file), dest)

    logger.info("Testing installation")
    success = True
    if find_spec("information_reconciliation") is None:
        logger.error("information_reconciliation module is not found")
        success = False
    else:
        logger.info("Installation is successful")

    return success


def uninstall_ir_for_cvqkd() -> bool:
    """
    Uninstall IR_for_CVKQD.

    Returns:
        bool: True in case of successful installation, False otherwise.
    """
    logger.info("Checking if IR_for_CVQKD is installed")
    specs = find_spec("information_reconciliation")
    if specs is None:
        logger.info("information_reconciliation is not installed. Doing nothing.")
        return True

    logger.info("Deleting shared library %s from python library", specs.origin)

    assert specs.origin is not None

    os.remove(specs.origin)

    if os.path.isdir("deps"):
        logger.info("deps directory present. Removing.")
        shutil.rmtree("deps")
        logger.info("deps directory deleted.")

    logger.info(
        "Deleted library. Checking if information_reconciliation is still present."
    )

    if find_spec("information_reconciliation") is None:
        logger.info("information_reconciliation not present.")
        return True
    logger.error("Error during uninstallation.")
    return False


def install_cryptomite() -> bool:
    """
    Install cryptomite from https://github.com/CQCL/cryptomite.

    Install cryptomite from pypi is preferred, but at te time of writing
    this code, cryptomite is has not wheel for python3.13 and linux.

    Returns:
        bool: True if the installation is successful, False otherwise.
    """
    logger.warning("Installation of cryptomite should preferably done using pypi.")
    with tempfile.TemporaryDirectory() as deps:
        logger.debug("Created directory %s", str(deps))

        os.chdir(deps)

        logger.info("Cloning cryptomite")

        subprocess.run(["git", "clone", CM_REPO], check=True)

        os.chdir("cryptomite")

        subprocess.run(["pip", "install", "."], check=True)

        logger.info("Testing installation")

        success = True
        if find_spec("cryptomite") is None:
            logger.error("cryptomite module is not found")
            success = False
        else:
            logger.info("Installation is successful")

        logger.info("Cleaning %s directory", str(deps))
    return success


def uninstall_cryptomite() -> bool:
    """
    Uninstall cryptomite.

    Returns:
        bool: True in case of successful installation, False otherwise.
    """
    logger.info("Checking if cryptomite is installed")
    specs = find_spec("cryptomite")
    if specs is None:
        logger.info("cryptomite is not installed. Doing nothing.")
        return True

    logger.info("Uninstalling cryptomite")

    subprocess.run(["pip", "uninstall", "cryptomite"], check=True)

    logger.info("Checking if cryptomite is still present.")

    if find_spec("cryptomite") is None:
        logger.info("cryptomite not present.")
        return True
    logger.error("Error during uninstallation.")
    return False
