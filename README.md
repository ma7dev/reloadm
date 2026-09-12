# reloadm

`reloadm` gives notebooks and Python REPLs an explicit, predictable way to
reload edited modules. It accepts a module, dotted module name, function,
method, or class. Unlike a plain `importlib.reload`, it can also refresh parent
packages after their children so package-level re-exports point to the new
objects.

The core package is typed and dependency-free.

## The problem it solves

Suppose `shop/__init__.py` re-exports a function:

```python
from .pricing import calculate_total
```

After editing `shop/pricing.py`, reload the child and then its parents:

```python
import shop.pricing
from reloadm import reload

pricing = reload(shop.pricing, include_parents=True)
```

`reloadm` processes `shop.pricing` before `shop`, so both
`pricing.calculate_total` and `shop.calculate_total` use the new definition.
Parent cascading is disabled by default because package initializers can have
side effects:

```python
pricing = reload(shop.pricing)
```

## Installation

Install the latest version directly from GitHub:

```bash
python -m pip install "reloadm @ git+https://github.com/ma7dev/reloadm.git"
```

Install the optional IPython integration with:

```bash
python -m pip install "reloadm[ipython] @ git+https://github.com/ma7dev/reloadm.git"
```

`reloadm` supports Python 3.10 through 3.14.

## Choose the right tool

| Tool | Best for | Parent re-exports | Automatic |
| --- | --- | --- | --- |
| `importlib.reload` | One known module | No | No |
| IPython `%autoreload` | Continuous notebook development | Attempts object upgrades | Yes |
| `reloadm` | Explicit, inspectable reloads in any REPL | Optional child-first repair | No |

Use `%autoreload` when you want broad automatic behavior. Use `reloadm` when
you want to choose exactly when and what is reloaded.

## API examples

Reload one module:

```python
from reloadm import reload

module = reload("shop.pricing")
```

Preview a cascade without importing or executing anything:

```python
from reloadm import plan

plan("shop.pricing.rules", include_parents=True).modules
# ('shop.pricing.rules', 'shop.pricing', 'shop')
```

Reload several edited modules while deduplicating shared parents:

```python
from reloadm import reload_many

result = reload_many(
    ["shop.pricing", "shop.discounts"],
    include_parents=True,
)

print(result.reloaded)
print(result.duration_seconds)
print(dict(result.target_files))
```

## IPython magic

```python
%load_ext reloadm.ipython
%reloadm shop.pricing
%reloadm --parents shop.pricing shop.discounts
```

The magic prints each module as it reloads and returns a structured
`ReloadResult`.

## Important limits

Python module reloading changes code inside an existing module object; it does
not rebuild the whole running program.

- Existing class instances still use their old class definitions.
- Local names created by `from module import name` remain stale unless their
  owning parent package is cascaded or they are imported again.
- Module-level side effects run again.
- Reloading extension modules, `builtins`, or `__main__` is unsupported.
- Decorators can hide a callable's true owner module.
- Reloading is not thread-safe. Use it only in a controlled interactive loop.
- If a cascade fails, earlier modules may already have reloaded. Inspect
  `ReloadError.reloaded`.

See the [API guide](docs/api.md), [usage guide](docs/usage.md), and
[executable notebook](examples/reloadm_demo.ipynb).

## Development

```bash
uv sync --locked --all-extras
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m build
uv run python -m twine check dist/*
```

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes are recorded in
[CHANGELOG.md](CHANGELOG.md).

## License

MIT
