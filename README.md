# qosst-pp

<center>

![QOSST Logo](qosst_logo_full.png)

<a href='https://qosst-pp.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/qosst-pp/badge/?version=latest' alt='Documentation Status' />
</a>
<a href="https://github.com/qosst/qosst-pp/blob/main/LICENSE"><img alt="Github - License" src="https://img.shields.io/github/license/qosst/qosst-pp"/></a>
<a href="https://github.com/qosst/qosst-pp/releases/latest"><img alt="Github - Release" src="https://img.shields.io/github/v/release/qosst/qosst-pp"/></a>
<a href="https://pypi.org/project/qosst-pp/"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/qosst-pp"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/pylint-dev/pylint"><img alt="Linting with pylint" src="https://img.shields.io/badge/linting-pylint-yellowgreen"/></a>
<a href="https://mypy-lang.org/"><img alt="Checked with mypy" src="https://www.mypy-lang.org/static/mypy_badge.svg"></a>
<a href="https://img.shields.io/pypi/pyversions/qosst-pp">
    <img alt="Python Version" src="https://img.shields.io/pypi/pyversions/qosst-pp">
</a>
<img alt="Docstr coverage" src=".docs_badge.svg" />
</center>
<hr/>

This project is part of [QOSST](https://github.com/qosst/qosst).

## Features

`qosst-pp` is the module of QOSST in charge of error reconciliation and privacy amplification. In particular, it includes:

* Functions handling the socket messages for error reconciliation, using [IR_for_CVQKD](https://github.com/erdemeray/IR_for_CVQKD);
* Extractors for privacy amplification and associated functions for Alice and Bob, using [Cryptomite](https://github.com/CQCL/cryptomite).

## Installation

The module can be installed with the following command:

```console
pip install qosst-pp
```

It is also possible to install it directly from the github repository:

```console
pip install git+https://github.com/qosst/qosst-pp
```

It also possible to clone the repository before and install it with pip or poetry

```console
git clone https://github.com/qosst/qosst-pp
cd qosst-pp
poetry install
pip install .
```

## Documentation

The whole documentation can be found at https://qosst-pp.readthedocs.io/en/latest/

## License

As for all submodules of QOSST, `qosst-pp` is shipped under the [Gnu General Public License v3](https://www.gnu.org/licenses/gpl-3.0.html).

## Contributing

Contribution are more than welcomed, either by reporting issues or proposing merge requests. Please check the contributing section of the [QOSST](https://github.com/qosst/qosst) project fore more information.