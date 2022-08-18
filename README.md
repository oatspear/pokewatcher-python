# pokewatcher-python

Scripts to watch Pokémon games being played on an emulator

- [Package Structure](#package-structure)
- [Tooling](#tooling)

## Package Structure

The package provides a `src` directory, under which Python modules and packages sit.

Tests are placed under the `tests` directory, and documentation under the `docs` directory.

## Tooling

This package sets up various `tox` environments for static checks, testing, building and publishing.
It is also configured with `pre-commit` hooks to perform static checks and automatic formatting.

If you do not use `tox`, you can build the package with `build` and install a development version with `pip`.

Assume `cd` into the repository's root.

To install the `pre-commit` hooks:

```bash
pre-commit install
```

To run type checking:

```bash
tox -e typecheck
```

To run linting tools:

```bash
tox -e lint
```

To run automatic formatting:

```bash
tox -e format
```

To run tests:

```bash
tox
```

To run manual tests:

```bash
tox -e debug
```

To build the package:

```bash
tox -e build
```

To build the package (with `build`):

```bash
python -m build
```

To build a standalone executable for the host platform (output in `./dist`):

```bash
tox -e exe
```

To clean the previous build files:

```bash
tox -e clean
```

To test package publication (publish to *Test PyPI*):

```bash
tox -e publish
```

To publish the package to PyPI:

```bash
tox -e publish -- --repository pypi
```

To install an editable version:

```bash
pip install -e .
```
