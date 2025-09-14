"""

```plantuml name="overview"
annotation Setup {
    + strategies : list[Sid] 
    + benchmarks : list[Bid] 
    + dataname : str
    + solver : SolverPy
    + db : DB
    + builder : Builder
    --
    + launch()
}

abstract class SolverPy {
    # plugins : Plugins
    --
    + {abstract} solve(problem, strategy) : Result
    + solved(result) : bool
}

abstract class Plugin <<plugin>> {
    # id : str
    --
    {abstract} + register(solver)
    --
    {abstract} + decorate()
    {abstract} + update()
    {abstract} + translate()
    {abstract} + finished()
}

class SolverTask {
   + solver : SolverPy
   + benchmark : Bid
   + problem : str
   + strategy : Sid
   --
   + run() : Result
}

class DB {
       # providers : Providers
       --
       + commit()
       + connect(benchmark, strategy)
       + query(tasks) : Results
       + store(tasks, results)
}

abstract class Builder {
      # dataname : str
      {abstract} + strategies : list[Sid] 
      --
      {abstract} + build()
      {abstract} + apply(strategy, model) : list[Sid]
}

abstract class Trains <<plugin>> {
       # dataname : str
       --
       {abstract} # extract()
       + finished()
       {abstract} + compress()
       {abstract} + merge()
}

abstract class Provider {
       # benchmark : Bid
       # strategy : Sid
       --
       {abstract} + commit()
       {abstract} + query(task) : Result
       {abstract} + store(task, result)
}



' Relationships
Setup --o "1" SolverPy 
Setup -down-o "1" DB 
Setup --o "1" Builder
Builder --o "1" Trains : uses
SolverPy --o "*" Plugin : registers
DB --o "*" Provider : connects
' DB -right-> Builder
DB .left.o "*" SolverTask : "    stores   "
SolverTask -left-o "1" SolverPy 

' ' Notes
note top of Setup : Collection of experiment settings.

note bottom of SolverTask
Represent a solver task 
with results stored in DB.
end note

note top of SolverPy
Generic solver interface 
compatible with DB.
end note

note bottom of DB
Persistent DB of results.
Stores results of solver tasks.
end note

note bottom of Trains
Extraction and management 
of training data. Implemented
as a solver plugin.
end note
```

"""

