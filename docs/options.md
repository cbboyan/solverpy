# SolverPy Options

+ An *option* is identified by its string name, and represents a boolean yes/no value.
+ Put the option name into the string list under the key`"options"` in the setup.
+ Use `no-`option, like `no-compress`, to set the option to `no`

|option|description|default|
|------|-----------|-------|
|`compress`|Compress output files (outputs, trains).|yes|
|`flatten`|Put all output files in a single directory (replace `/` with `_._`).|yes|
|`compress-trains`|Compress trains.|yes|
|`debug-trains`|Dump training data for each file separately.|no|

