import time as _time
import resource
from typing import Any, TYPE_CHECKING

from ..decorator import Decorator

if TYPE_CHECKING:
   from ....tools.typing import Result


class Time(Decorator):
   """Measure wall-clock, user, and sys time using Python's stdlib.

   Snapshots `time.perf_counter()` and `resource.getrusage(RUSAGE_CHILDREN)`
   in `decorate()` (just before the subprocess) and computes deltas in
   `update()` (just after).  Three keys are added to the result:

   - `realtime` — elapsed wall-clock time (seconds)
   - `usertime` — user-mode CPU time of child processes (seconds)
   - `systime`  — kernel-mode CPU time of child processes (seconds)
   - `runtime`  — `realtime - systime` (canonical solve time)

   The solver command is not modified, so no timing lines appear in the
   raw solver output.
   """

   def __init__(self, **kwargs):
      Decorator.__init__(self, **kwargs)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      """Snapshot start times; return *cmd* unchanged."""
      del instance, strategy  # unused arguments
      self._t0_wall = _time.perf_counter()
      r = resource.getrusage(resource.RUSAGE_CHILDREN)
      self._t0_user = r.ru_utime
      self._t0_sys = r.ru_stime
      return cmd

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      """Compute time deltas and populate *result*."""
      del instance, strategy, output  # unused arguments
      wall = _time.perf_counter() - self._t0_wall
      r = resource.getrusage(resource.RUSAGE_CHILDREN)
      user = r.ru_utime - self._t0_user
      sys_ = r.ru_stime - self._t0_sys
      result["realtime"] = wall
      result["usertime"] = user
      result["systime"] = sys_
      result["runtime"] = wall - sys_
