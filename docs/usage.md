# Notebook and REPL workflow

## A focused edit-run loop

1. Import your project module normally.
2. Edit the module's source file.
3. Call `reloadm.reload(module)`.
4. Call code through the returned module.

```python
import my_project.scoring
from reloadm import reload

# Edit my_project/scoring.py, then:
scoring = reload(my_project.scoring)
scoring.score(records)
```

Calling through the returned module avoids a common trap:

```python
from my_project.scoring import score

reload(score)
score(records)  # This name still points to the old function.

from my_project.scoring import score  # Rebind it explicitly.
score(records)
```

## Choosing parent behavior

Keep `include_parents=True` when parent `__init__.py` files re-export values or
perform registration. Use `False` when parent imports are expensive or have
side effects and only the leaf module changed.

## Handling partial failure

```python
from reloadm import ReloadError, reload

try:
    reload("my_project.scoring")
except ReloadError as error:
    print("failed:", error.module_name)
    print("already reloaded:", error.reloaded)
    raise
```
