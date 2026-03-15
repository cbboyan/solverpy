"""

# Strategy identifiers (sid)

Strategy is a collection of solver options, parameters, settings, etc., that
influence the space search behavior of the solver. In SolverPy, this collection must be
stored in a file and placed inside the `strats` database directory, by default
`solverpy_db/strats` (see the [`db`][solverpy.benchmark.db] module). The file
name inside the `strats` directory is called the _strategy id_ (`sid`). The
content of the file is a solver-specific _strategy definition_ that is passed to
the [`Solver.solve`][solverpy.solver.solver.Solver.solve] method.

Example:
   For [`E`][solverpy.solver.atp.eprover.E] Prover, you can have the file
   `solverpy_db/strats/auto` with the following content:

   ```
   --auto-schedule
   ```

   Then `--auto-schedule` is the strategy definition while `auto` is its
   strategy id. You can now use `auto` in `sidlist` to reference the strategy
   in experiment setup [`Setup`][solverpy.setups.setup.Setup] with
   [`E`][solverpy.solver.atp.eprover.E] Prover.

Note:
   As opposed to a benchmark identifier [`bid`][solverpy.benchmark.path.bids],
   a strategy identifier `sid` can not contain `/` characters.

## Parametric Strategies

Some solvers support parametric strategies with variable slots in the strategy
definition.  The syntax for variable slots is as follows:

```
@@@ var : value @@@
```

where `var` is the variable name and `value` is its default value.

Note:
   Names `var` and `value` can not contain characters `@`, `:`, or space.

The value of a variable can be overridden in the strategy identifier
using the following format:

```
sid@var1=value1:var2=value2
```

Here `sid` still refers to the base strategy id, while `var1=value1` and
`var2=value2` are different variable assignments. Any number of `:`-separated
variable assignments can be provided in the strategy id.

Example:
   For [`E`][solverpy.solver.atp.eprover.E] Prover, you can have a parametric
   strategy `gen` with the following definition:

   ```
   --enigmatic-gen-threshold=@@@ thrgen : 0.1 @@@
   ```

   Then the strategy id (sid)

   ```
   gen@thrgen=0.5
   ```

   results in the following strategy definition:

   ```
   --enigmatic-gen-threshold=0.5
   ```

See Also:
   See the [`Sid`][solverpy.solver.plugins.db.sid.Sid] solver plugin that
   automatically translates strategy ids to strategy definitions. For more
   details about solver-specific strategy formats, see concrete solvers
   implemented in the [`solver`][solverpy.solver.solver] module.
   

# Module content

Note:
   In the code base, arguments/variables `sid` refer to the strategy identifiers,
   while `strategy` refers to the strategy definition.
   
"""

import os
import re

from . import bids

NAME = "strats"

ARGUMENT = re.compile(r"@@@\s*([^@: ]*)\s*:\s*([^@: ]*)\s*@@@")

def path(sid: str) -> str:
   """Return the path to the strategy file."""
   f_sid = sid.split("@")[0] if ("@" in sid) else sid
   return os.path.join(bids.dbpath(NAME), f_sid)

def load(sid: str) -> str:
   """Load the strategy definition."""
   return open(path(sid)).read().strip()

def save(sid: str, strategy: str) -> None:
   """Save the strategy definition."""
   f_sid = path(sid)
   os.makedirs(os.path.dirname(f_sid), exist_ok=True)
   open(f_sid, "w").write(strategy.strip())

def name(sid: str) -> str:
   return sid.replace("/", "--")

def unspace(strategy: str) -> str:
   """Merge multiple white spaces into a single space."""
   return " ".join(x for x in strategy.split() if x)

def split(sid: str) -> tuple[str, dict[str, str]]:
   """Split sid into the strategy file and arguments."""
   args = {}
   if "@" in sid:
      (sid, args) = sid.split("@")
      args = args.split(":")
      args = [x.split("=") for x in args]      
      args = {x.strip():y.strip() for (x,y) in args}
   return (sid, args)

def instatiate(strategy: str, args: dict[str, str]) -> str:
   """Instantiate the strategy with arguments."""
   args0 = defaults(strategy)
   args0.update(args)
   ret = ARGUMENT.sub(lambda mo: args0[mo.group(1)], strategy)
   return ret

def defaults(strategy: str) -> dict[str, str]:
   """Extract variables and default values from the strategy definition."""
   ret = ARGUMENT.findall(strategy)
   ret = {x.strip():y.strip() for (x,y) in ret}
   return ret

def fmt(base: str, args: dict[str, str]) -> str:
   """Format strategy file with arguments."""
   args0 = ":".join(f"{x}={args[x]}" for x in sorted(args))
   return f"{base}@{args0}"

def normalize(sid: str) -> str:
   """Remove arguments from sid which set default values and sort arguments."""
   strategy = load(sid)
   defs = defaults(strategy)
   (sid, args) = split(sid)
   args = {x:y for (x,y) in args.items() if y != defs[x]}
   return fmt(sid, args)
   
