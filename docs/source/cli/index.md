# Command Line Interface (CLI)

The `qosst-pp` package is shipped with a Command Line Interface (CLI) to execute one particular command. This is the install command to install [IR_for_CVQKD](https://github.com/erdemeray/IR_for_CVQKD) and [Cryptomite](https://github.com/CQCL/cryptomite).

[IR_for_CVQKD](https://github.com/erdemeray/IR_for_CVQKD) is not on PyPi and requires cmake and make to be built. The script performs the installation automatically by building the shared library and placing it in the site-package. It performs roughly the same operations as the install.sh script available on the github of qosst-pp.

[Cryptomite](https://github.com/CQCL/cryptomite) should be available on Pypi but not for linux and python3.13. The preferred way of installing cryptomite is Pypi.


```{warning}

This install script is only proposed as an experimental feature, and manual installation is recommended in case the script fails.
```

The extended CLI documentation is available [here](./documentation.md) and the API documentation of the CLI is available [here](./api.md).

## Get help

You can get help with the `-h` or `--help` flag:

```{command-output} qosst-pp -h
```

This displays the available command. You can also get help on a specific command:

```{command-output} qosst-pp install -h
```

## Get the version

You can get the version of the script (which is the same as the version of the `qosst-pp` package) with the `--version` flag:

```{command-output} qosst-pp --version
```

## Install command

`IR_for_CVQKD` can be installed with

```{prompt} bash
qosst-pp install IR_for_CVQKD
```

and uninstalled with 

```{prompt} bash
qosst-pp uninstall IR_for_CVQKD
```

`cryptomite` can be installed with 


```{prompt} bash
qosst-pp install cryptomite
```

and uninstalled with 

```{prompt} bash
qosst-pp uninstall cryptomite
```