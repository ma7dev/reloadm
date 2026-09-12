# reloadm

`reloadm` shortens the edit-run loop in a Python notebook or REPL. Give it a
module, module name, or function and it reloads the owning module. For a nested
module, it can reload the package chain from the outside in.

The package is intentionally small, typed, and dependency-free.

## When it helps

Suppose you are developing `acme.pricing.rules` while exploring results in a
notebook. After editing the source, reload the module without restarting the
kernel:

```python
import acme.pricing.rules
from reloadm import reload

rules = reload(acme.pricing.rules)
rules.calculate_total(order)
```

You can also start from a module name or a function:

```python
from acme.pricing.rules import calculate_total
from reloadm import reload

reload("acme.pricing.rules")
reload(calculate_total)
```

By default, the second example reloads `acme`, then `acme.pricing`, then
`acme.pricing.rules`. This helps when package `__init__.py` files export objects
from child modules. To reload only the target:

```python
reload(calculate_total, include_parents=False)
```

## Installation

The repository is private and is not automatically published to PyPI. Install
it from a local checkout:

```bash
python -m pip install /path/to/reloadm
```

For development:

```bash
uv sync --locked --all-extras
uv run pytest
```

`reloadm` supports Python 3.9 through 3.13.

## API

```python
reloadm.reload(target, verbose=False, *, include_parents=True) -> ModuleType
```

| Argument | Meaning |
|---|---|
| `target` | Module object, importable module name, or Python function/method |
| `verbose` | Write each reloaded module name to standard error |
| `include_parents` | Reload dotted package parents before the target |

The return value is the reloaded target module. Import or reload failures raise
`reloadm.ReloadError`. Its `module_name` attribute identifies the failing module,
and `reloaded` lists modules completed before the failure.

See [the API guide](docs/api.md) and [the notebook/REPL workflow](docs/usage.md)
for more examples.

## Important limits

Python reloads code inside an existing module object; it does not rebuild the
whole running program.

- Names imported with `from module import name` keep pointing to their old
  objects. Import them again after reloading.
- Existing class instances still use their old class definition.
- Module-level side effects run again.
- Reloading extension modules, `builtins`, or `__main__` is unsupported.
- If one module fails, earlier parents may already have been reloaded. Inspect
  `ReloadError.reloaded` when recovery matters.

For automatic notebook reloading, IPython's `%autoreload` extension may be a
better fit. `reloadm` is useful when you want an explicit, dependency-free call
that also understands a package hierarchy.

## Development

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m build
uv run python -m twine check dist/*
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow. Changes are tracked
in [CHANGELOG.md](CHANGELOG.md).

## License

MIT
