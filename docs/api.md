# API reference

## `reloadm.reload`

```python
reload(target, verbose=False, *, include_parents=False) -> ModuleType
```

Reload one module and return it. `target` may be a module object, dotted module
name, Python function, method, or class whose `__module__` identifies its
owner. Parent cascading is opt-in. When enabled, the target reloads first,
followed by parents from nearest to outermost.

## `reloadm.plan`

```python
plan(targets, *, include_parents=False) -> ReloadPlan
```

Compute a deterministic reload order without importing or executing any
module. `targets` may be one target or an iterable. Duplicate targets and
shared parents are scheduled once.

| Field | Meaning |
| --- | --- |
| `requested` | Module names in the original request, including duplicates |
| `modules` | Deduplicated execution order |

## `reloadm.reload_many`

```python
reload_many(targets, verbose=False, *, include_parents=False) -> ReloadResult
```

Reload several targets. Deeper modules run before their parents so a parent
re-export observes every new child definition, even when the parent was also
requested explicitly.

| Field | Meaning |
| --- | --- |
| `requested` | Resolved names in the original request |
| `planned` | Deduplicated planned order |
| `reloaded` | Successfully completed modules |
| `target_files` | `(module_name, absolute_file_or_none)` pairs |
| `duration_seconds` | Reload execution duration |

## `reloadm.ReloadError`

Import and reload failures are wrapped in `ReloadError`; the original exception
is available as `__cause__`.

| Attribute | Meaning |
| --- | --- |
| `module_name` | Module that could not be imported or reloaded |
| `reloaded` | Modules completed before the failure |

Invalid target types raise `TypeError`. Empty names or target collections raise
`ValueError`.
