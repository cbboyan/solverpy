import os
import logging

from ..benchmark.path import bids
from ..solver.object import SolverPyObj

NAME = "models"

logger = logging.getLogger(__name__)


class Builder(SolverPyObj):
   """Build the model from the training samples."""

   def __init__(self, dataname: str):
      """Construct the builder and store the dataname."""
      SolverPyObj.__init__(self, dataname=dataname)
      self._strats = []
      self._dataname = dataname

   def path(self) -> str:
      """Return the model filename."""
      return os.path.join(bids.dbpath(NAME), self._dataname)

   def reset(self, dataname: str) -> None:
      """Reset the dataname, for example, when a new loop is initiated."""
      self._dataname = dataname

   def build(self) -> None:
      """Build the model(s). Save the list of new strategies `self._strats`."""
      raise NotImplementedError()

   def apply(self, sid: str, model: str) -> list[str]:
      """Combine the `model` with strategy `sid`."""
      del sid, model
      raise NotImplementedError()

   @property
   def strategies(self):
      """Return all created strategies."""
      return self._strats

   def applies(self, sidlist: list[str], model: str) -> list[str]:
      """Combine the `model` with several strategies `sidlist`."""
      new = []
      for ref in sidlist:
         new.extend(self.apply(ref, model))
      return new

