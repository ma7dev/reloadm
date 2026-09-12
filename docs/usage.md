# Notebook and REPL workflow

## Focused reload

Import a module, edit its source, then explicitly reload it:

```python
import my_project.scoring
from reloadm import reload

scoring = reload(my_project.scoring)
scoring.score(records)
```

Calling through the returned module avoids a common trap:

```python
from my_project.scoring import score

reload(score)
score(records)  # Still the old local function object.

from my_project.scoring import score  # Rebind explicitly.

score(records)
```

## Repair package re-exports

If `my_project/__init__.py` contains `from .scoring import score`, opt into a
child-first parent cascade:

```python
reload("my_project.scoring", include_parents=True)
```

The order is `my_project.scoring`, then `my_project`. The parent initializer
runs after the child and therefore binds the new `score` object.

## Preview before executing

Package initializers may connect to services, register plugins, or mutate
global state. Preview a cascade first:

```python
from reloadm import plan

for module_name in plan("my_project.scoring", include_parents=True).modules:
    print(module_name)
```

## Batch related edits

```python
from reloadm import reload_many

result = reload_many(
    ["my_project.scoring", "my_project.validation"],
    include_parents=True,
)
```

Shared parents reload once, after both children.

## Use the IPython magic

```python
%load_ext reloadm.ipython
%reloadm my_project.scoring
%reloadm --parents my_project.scoring my_project.validation
```

## Handle partial failure

```python
from reloadm import ReloadError, reload

try:
    reload("my_project.scoring", include_parents=True)
except ReloadError as error:
    print("failed:", error.module_name)
    print("already reloaded:", error.reloaded)
    raise
```

Reloading cannot roll back module side effects or restore earlier object state.
Restart the interpreter when a clean process matters.
