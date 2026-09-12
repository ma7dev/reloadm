# API reference

## `reloadm.reload`

```python
reload(target, verbose=False, *, include_parents=True) -> ModuleType
```

Resolve and reload a module. `target` may be an imported module, a dotted module
name such as `"package.feature.rules"`, or a Python function or method whose
`__module__` identifies its owner.

With `include_parents=True`, reload order is outermost to innermost. For
`package.feature.rules`, the order is `package`, `package.feature`, then
`package.feature.rules`. The return value is the target module returned by
`importlib.reload`.

## `reloadm.ReloadError`

Import and reload failures are wrapped in `ReloadError` with the original
exception available as `__cause__`.

| Attribute | Meaning |
|---|---|
| `module_name` | Module that could not be imported or reloaded |
| `reloaded` | Module names successfully reloaded before the failure |

Invalid target types raise `TypeError`, and an empty string raises `ValueError`.
