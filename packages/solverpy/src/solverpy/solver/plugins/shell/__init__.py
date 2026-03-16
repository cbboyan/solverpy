"""
# Shell plugins

Shell plugins control how the solver subprocess is launched: building
resource-limit arguments, wrapping the command with `timeout`, and
measuring wall-clock time with `/usr/bin/env time`.

```plantuml name="solver-plugins-shell"

abstract class solverpy.solver.plugins.decorator.Decorator
abstract class solverpy.solver.plugins.translator.Translator

class solverpy.solver.plugins.shell.limits.Limits extends solverpy.solver.plugins.decorator.Decorator
solverpy.solver.plugins.shell.limits.Limits extends solverpy.solver.plugins.translator.Translator

class solverpy.solver.plugins.shell.timeout.Timeout extends solverpy.solver.plugins.decorator.Decorator
class solverpy.solver.plugins.shell.time.Time extends solverpy.solver.plugins.decorator.Decorator

```

| Plugin | Description |
|---|---|
| [`Limits`][solverpy.solver.plugins.shell.limits.Limits] | Parses the limit string (e.g. `T5-M2048`) and appends solver-specific CLI flags; can also inject limits via stdin |
| [`Timeout`][solverpy.solver.plugins.shell.timeout.Timeout] | Prepends `timeout --kill-after=15 --foreground N` to enforce a hard wall-clock cutoff |
| [`Time`][solverpy.solver.plugins.shell.time.Time] | Prepends `/usr/bin/env time -p` to measure real/user/sys time; populates `runtime` in the result |

"""

from .limits import Limits
from .timeout import Timeout
from .time import Time

__all__ = ["Limits", "Timeout", "Time"]

