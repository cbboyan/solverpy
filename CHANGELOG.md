# Change Log

## Unreleased changes (2026-06-17)

* docs: add experiment refactor task notes [[details](https://github.com/cbboyan/solverpy/commit/) | [browse](https://github.com/cbboyan/solverpy/tree/)]
* test: cover asymmetrical loop setup paths [[details](https://github.com/cbboyan/solverpy/commit/0f3ac03) | [browse](https://github.com/cbboyan/solverpy/tree/0f3ac03)]
* docs: archive setup/evalset refactor regressions [[details](https://github.com/cbboyan/solverpy/commit/3f3051c) | [browse](https://github.com/cbboyan/solverpy/tree/3f3051c)]
* fix: finish setup/evalset refactor [[details](https://github.com/cbboyan/solverpy/commit/ed4b805) | [browse](https://github.com/cbboyan/solverpy/tree/ed4b805)]
* fix: Fixed evaluation/looping for E after refactor [[details](https://github.com/cbboyan/solverpy/commit/4bdcd7c) | [browse](https://github.com/cbboyan/solverpy/tree/4bdcd7c)]
* fix: normalize experiment setups [[details](https://github.com/cbboyan/solverpy/commit/99e852b) | [browse](https://github.com/cbboyan/solverpy/tree/99e852b)]
* fix: warn on non-zero tuner exit [[details](https://github.com/cbboyan/solverpy/commit/4c4fe3e) | [browse](https://github.com/cbboyan/solverpy/tree/4c4fe3e)]
* test: align slow and learn expectations [[details](https://github.com/cbboyan/solverpy/commit/0931500) | [browse](https://github.com/cbboyan/solverpy/tree/0931500)]
* feat(log): route worker logs to parent via persistent Manager queue [[details](https://github.com/cbboyan/solverpy/commit/dc1d1b4) | [browse](https://github.com/cbboyan/solverpy/tree/dc1d1b4)]
* refactor(setup): extract Evalset, Runtime, Managed; move talker into Setup [[details](https://github.com/cbboyan/solverpy/commit/202f6df) | [browse](https://github.com/cbboyan/solverpy/tree/202f6df)]
* refactor(setup): plan Dataset split and init ordering [[details](https://github.com/cbboyan/solverpy/commit/7782d6f) | [browse](https://github.com/cbboyan/solverpy/tree/7782d6f)]
* fix(autotune): preload validation data [[details](https://github.com/cbboyan/solverpy/commit/4989b84) | [browse](https://github.com/cbboyan/solverpy/tree/4989b84)]
* fix(autotune): isolate repeated tuning phases [[details](https://github.com/cbboyan/solverpy/commit/16eb4d3) | [browse](https://github.com/cbboyan/solverpy/tree/16eb4d3)]
* feat(smt): add llm2smt solver [[details](https://github.com/cbboyan/solverpy/commit/c3fc5fc) | [browse](https://github.com/cbboyan/solverpy/tree/c3fc5fc)]
* fix(autotune): evaluate full tuning benchmark [[details](https://github.com/cbboyan/solverpy/commit/a065ca2) | [browse](https://github.com/cbboyan/solverpy/tree/a065ca2)]
* docs: finish setup-key rename [[details](https://github.com/cbboyan/solverpy/commit/e1f7b6b) | [browse](https://github.com/cbboyan/solverpy/tree/e1f7b6b)]
* feat(report): add training data stats [[details](https://github.com/cbboyan/solverpy/commit/9e040a9) | [browse](https://github.com/cbboyan/solverpy/tree/9e040a9)]
* fix(autotune): avoid retaining raw training data [[details](https://github.com/cbboyan/solverpy/commit/04a44aa) | [browse](https://github.com/cbboyan/solverpy/tree/04a44aa)]
* fix: fork tuner before starting listener threads [[details](https://github.com/cbboyan/solverpy/commit/7198dab) | [browse](https://github.com/cbboyan/solverpy/tree/7198dab)]
* fix: clean up interrupted tuner process groups [[details](https://github.com/cbboyan/solverpy/commit/2a86410) | [browse](https://github.com/cbboyan/solverpy/tree/2a86410)]
* feat: log resource usage during learning loops [[details](https://github.com/cbboyan/solverpy/commit/8441118) | [browse](https://github.com/cbboyan/solverpy/tree/8441118)]
* fix: clean up multiprocessing lifecycle [[details](https://github.com/cbboyan/solverpy/commit/082fd52) | [browse](https://github.com/cbboyan/solverpy/tree/082fd52)]
* refactor: single shared talker per session; EvalTalker/LoopTalker replace LogTalker headless [[details](https://github.com/cbboyan/solverpy/commit/e128be9) | [browse](https://github.com/cbboyan/solverpy/tree/e128be9)]
* refactor: make Talker() a concrete no-op, remove Talker|None and if talker: guards [[details](https://github.com/cbboyan/solverpy/commit/f315271) | [browse](https://github.com/cbboyan/solverpy/tree/f315271)]
* refactor: rename SolverTalker→EvalTalker, TuneTalker→LoopTalker, move LoopTalker to solverpy-learn [[details](https://github.com/cbboyan/solverpy/commit/d22de98) | [browse](https://github.com/cbboyan/solverpy/tree/d22de98)]
* fix: suppress eval log messages during ATP evaluation inside tuning [[details](https://github.com/cbboyan/solverpy/commit/c835bbf) | [browse](https://github.com/cbboyan/solverpy/tree/c835bbf)]
* fix: keep tuning task bars visible after completion (leave=True) [[details](https://github.com/cbboyan/solverpy/commit/cca13c3) | [browse](https://github.com/cbboyan/solverpy/tree/cca13c3)]
* refactor: move child-side logger calls to talker.debug(), promote LogTalker.debug [[details](https://github.com/cbboyan/solverpy/commit/20dace5) | [browse](https://github.com/cbboyan/solverpy/tree/20dace5)]
* feat: route child/worker logging through queue to parent handlers [[details](https://github.com/cbboyan/solverpy/commit/68cdf4a) | [browse](https://github.com/cbboyan/solverpy/tree/68cdf4a)]
* refactor: replace TuneTalker proxy with RemoteTalker in tuning pipeline [[details](https://github.com/cbboyan/solverpy/commit/3c055cc) | [browse](https://github.com/cbboyan/solverpy/tree/3c055cc)]
* refactor: pass talker explicitly to build.score(), remove builder.talker [[details](https://github.com/cbboyan/solverpy/commit/250841b) | [browse](https://github.com/cbboyan/solverpy/tree/250841b)]
* refactor: rename all Talker event methods with eval_/tune_/build_ prefixes [[details](https://github.com/cbboyan/solverpy/commit/4f93801) | [browse](https://github.com/cbboyan/solverpy/tree/4f93801)]
* docs: add talkers.md — method summary, per-talker behaviour, and call sites [[details](https://github.com/cbboyan/solverpy/commit/2affb52) | [browse](https://github.com/cbboyan/solverpy/tree/2affb52)]
* feat: add -f/--force alias to solverpy clean [[details](https://github.com/cbboyan/solverpy/commit/f9b9129) | [browse](https://github.com/cbboyan/solverpy/tree/f9b9129)]
* fix: route console logging through tqdm.write, fix tune bar and bar format [[details](https://github.com/cbboyan/solverpy/commit/33b4b17) | [browse](https://github.com/cbboyan/solverpy/tree/33b4b17)]
* refactor: move solverpy/tools/log and solverpy/talker into new solverpy/report [[details](https://github.com/cbboyan/solverpy/commit/bf23138) | [browse](https://github.com/cbboyan/solverpy/tree/bf23138)]
* docs: update TODO/DONE — RemoteTalker refactor plan, triage fixes [[details](https://github.com/cbboyan/solverpy/commit/6c5e19a) | [browse](https://github.com/cbboyan/solverpy/tree/6c5e19a)]
* feat: normalize tuning progress bars to two aligned bars [[details](https://github.com/cbboyan/solverpy/commit/d6086ce) | [browse](https://github.com/cbboyan/solverpy/tree/d6086ce)]
* fix: use fork (not forkserver) in @external decorator [[details](https://github.com/cbboyan/solverpy/commit/2d0d8de) | [browse](https://github.com/cbboyan/solverpy/tree/2d0d8de)]
* fix: normalize symlinks in rellink to avoid chain links across loops [[details](https://github.com/cbboyan/solverpy/commit/1b400be) | [browse](https://github.com/cbboyan/solverpy/tree/1b400be)]
* fix: run svm.compress() in external process to free scipy/numpy memory [[details](https://github.com/cbboyan/solverpy/commit/628fe8d) | [browse](https://github.com/cbboyan/solverpy/tree/628fe8d)]
* feat: complete talker package move, suppress atpeval report sections, add report extras [[details](https://github.com/cbboyan/solverpy/commit/b386dc4) | [browse](https://github.com/cbboyan/solverpy/tree/b386dc4)]
* feat: move talkers to solverpy.talker package, suppress atpeval report sections, add report extras [[details](https://github.com/cbboyan/solverpy/commit/b6bebe1) | [browse](https://github.com/cbboyan/solverpy/tree/b6bebe1)]
* fix: remove log_config/log_start/log_stop from RemoteTalker.REMOTES [[details](https://github.com/cbboyan/solverpy/commit/3932248) | [browse](https://github.com/cbboyan/solverpy/tree/3932248)]
* docs: document Talker hierarchy, process layers, and log queue in CLAUDE.md [[details](https://github.com/cbboyan/solverpy/commit/1a61237) | [browse](https://github.com/cbboyan/solverpy/tree/1a61237)]
* fix: RemoteTalker Manager lifetime and optional queue argument [[details](https://github.com/cbboyan/solverpy/commit/1c45c76) | [browse](https://github.com/cbboyan/solverpy/tree/1c45c76)]
* feat: replace RemoteTalker+AutotuneListener with TuneTalker [[details](https://github.com/cbboyan/solverpy/commit/26600be) | [browse](https://github.com/cbboyan/solverpy/tree/26600be)]
* feat: loop YAML support, clean log output, document Talker classes [[details](https://github.com/cbboyan/solverpy/commit/a51418d) | [browse](https://github.com/cbboyan/solverpy/tree/a51418d)]
* feat: improve report structure and summary/statuses tables [[details](https://github.com/cbboyan/solverpy/commit/6a7d7ed) | [browse](https://github.com/cbboyan/solverpy/tree/6a7d7ed)]
* feat: solverpy report command, progress bar alignment and style [[details](https://github.com/cbboyan/solverpy/commit/8e226d7) | [browse](https://github.com/cbboyan/solverpy/tree/8e226d7)]
* feat: use fully qualified class names in represent() and solver.name format [[details](https://github.com/cbboyan/solverpy/commit/f362ff6) | [browse](https://github.com/cbboyan/solverpy/tree/f362ff6)]
* fix: align repr() with represent() across all plugin classes [[details](https://github.com/cbboyan/solverpy/commit/21cea9f) | [browse](https://github.com/cbboyan/solverpy/tree/21cea9f)]
* feat: bundle setup YAMLs in data/setups/, copy to cwd on solverpy init [[details](https://github.com/cbboyan/solverpy/commit/e3a78ba) | [browse](https://github.com/cbboyan/solverpy/tree/e3a78ba)]
* feat: solverpy run/clean commands, fix log filename, document options [[details](https://github.com/cbboyan/solverpy/commit/3d31999) | [browse](https://github.com/cbboyan/solverpy/tree/3d31999)]
* feat: bundle strats as package data, implement solverpy init [solver] [[details](https://github.com/cbboyan/solverpy/commit/d874995) | [browse](https://github.com/cbboyan/solverpy/tree/d874995)]
* feat: number legend entries (s1..sN), use refs in summary/statuses/bars [[details](https://github.com/cbboyan/solverpy/commit/e8722b1) | [browse](https://github.com/cbboyan/solverpy/tree/e8722b1)]
* feat: represent() for Builder/Trains, combined setup+devels YAML, fix forkserver-in-fork-child [[details](https://github.com/cbboyan/solverpy/commit/d9ba556) | [browse](https://github.com/cbboyan/solverpy/tree/d9ba556)]
* docs: update TODO and DONE for reporter, prettytuner fork, RemoteTalker fix [[details](https://github.com/cbboyan/solverpy/commit/bd6bf5b) | [browse](https://github.com/cbboyan/solverpy/tree/bd6bf5b)]
* feat: add Reporter (.md sidecar), fix RemoteTalker pickling, switch prettytuner to fork [[details](https://github.com/cbboyan/solverpy/commit/e34f3bf) | [browse](https://github.com/cbboyan/solverpy/tree/e34f3bf)]
* fix: switch all multiprocessing contexts to forkserver, lazy-import numpy/scipy/sklearn [[details](https://github.com/cbboyan/solverpy/commit/66db01e) | [browse](https://github.com/cbboyan/solverpy/tree/66db01e)]
* fix: propagate flatten/compress from setup options to Reloader [[details](https://github.com/cbboyan/solverpy/commit/8a96647) | [browse](https://github.com/cbboyan/solverpy/tree/8a96647)]
* feat: complete Reloader implementation with Outputs.read() and setup integration [[details](https://github.com/cbboyan/solverpy/commit/fcfe339) | [browse](https://github.com/cbboyan/solverpy/tree/fcfe339)]
* feat: add unified `solverpy` CLI command, migrate scripts into packages [[details](https://github.com/cbboyan/solverpy/commit/2969787) | [browse](https://github.com/cbboyan/solverpy/tree/2969787)]
* feat: add posneg weight tuning phase 'w' to autotuner [[details](https://github.com/cbboyan/solverpy/commit/660d630) | [browse](https://github.com/cbboyan/solverpy/tree/660d630)]
* refactor: rename and regroup svm helpers with chunk_/raw_ prefixes [[details](https://github.com/cbboyan/solverpy/commit/0e30802) | [browse](https://github.com/cbboyan/solverpy/tree/0e30802)]
* fix: resolve pyright type errors in svm._stack_pairs [[details](https://github.com/cbboyan/solverpy/commit/b7b589d) | [browse](https://github.com/cbboyan/solverpy/tree/b7b589d)]
* feat: raw-chunk training data + parallel load/compress [[details](https://github.com/cbboyan/solverpy/commit/a652006) | [browse](https://github.com/cbboyan/solverpy/tree/a652006)]
* feat: chunked NPZ training data for 100 GB+ SVM-Light files [[details](https://github.com/cbboyan/solverpy/commit/6504297) | [browse](https://github.com/cbboyan/solverpy/tree/6504297)]
* fix: Python 3.14 multiprocessing + ENIGMATIC_ROOT model path issues [[details](https://github.com/cbboyan/solverpy/commit/0424a31) | [browse](https://github.com/cbboyan/solverpy/tree/0424a31)]
* fix: remove trailing commas from parser.add_argument calls in solverpy-autotune [[details](https://github.com/cbboyan/solverpy/commit/3c696bf) | [browse](https://github.com/cbboyan/solverpy/tree/3c696bf)]
* fix: rename --min_leaves and --max_leaves to --min-leaves and --max-leaves [[details](https://github.com/cbboyan/solverpy/commit/b177ede) | [browse](https://github.com/cbboyan/solverpy/tree/b177ede)]
* feat: add --early-stopping argument to solverpy-autotune [[details](https://github.com/cbboyan/solverpy/commit/e61cea0) | [browse](https://github.com/cbboyan/solverpy/tree/e61cea0)]
* feat: add solverpy-filter script to filter pos/neg training samples by ratio [[details](https://github.com/cbboyan/solverpy/commit/a8a45df) | [browse](https://github.com/cbboyan/solverpy/tree/a8a45df)]
* feat: extend solverpy-autotune with new arguments [[details](https://github.com/cbboyan/solverpy/commit/bff394d) | [browse](https://github.com/cbboyan/solverpy/tree/bff394d)]
* fix: Update output of solverpy-autotune. [[details](https://github.com/cbboyan/solverpy/commit/59bf816) | [browse](https://github.com/cbboyan/solverpy/tree/59bf816)]
* fix: update scripts to import from solverpy_learn after refactor [[details](https://github.com/cbboyan/solverpy/commit/8c7c8bb) | [browse](https://github.com/cbboyan/solverpy/tree/8c7c8bb)]
* refactor: split EVAL_CASES into EVAL_ATP and EVAL_SMT; premises tests ATP-only [[details](https://github.com/cbboyan/solverpy/commit/7978e51) | [browse](https://github.com/cbboyan/solverpy/tree/7978e51)]
* feat: add Proofs plugin to extract and save TPTP proofs and premises [[details](https://github.com/cbboyan/solverpy/commit/516672f) | [browse](https://github.com/cbboyan/solverpy/tree/516672f)]
* fix: set conf timeout to cutoff before runner construction in wrappers [[details](https://github.com/cbboyan/solverpy/commit/f83b017) | [browse](https://github.com/cbboyan/solverpy/tree/f83b017)]
* fix: eprover domain defaults match E binary defaults; clean() strips them; -H moved to end of args [[details](https://github.com/cbboyan/solverpy/commit/999e6fc) | [browse](https://github.com/cbboyan/solverpy/tree/999e6fc)]
* refactor: extract HoDomain from CoreDomain; parametric HeuristicDomain max_slots [[details](https://github.com/cbboyan/solverpy/commit/b06ffb0) | [browse](https://github.com/cbboyan/solverpy/tree/b06ffb0)]
* refactor: replace old wrapper scripts with new grackle scripts [[details](https://github.com/cbboyan/solverpy/commit/ff8a124) | [browse](https://github.com/cbboyan/solverpy/tree/ff8a124)]
* refactor: tests [[details](https://github.com/cbboyan/solverpy/commit/7e36f8c) | [browse](https://github.com/cbboyan/solverpy/tree/7e36f8c)]
* refactor: remove patch.dict SOLVERPY_BENCHMARKS from runner tests [[details](https://github.com/cbboyan/solverpy/commit/e1ec665) | [browse](https://github.com/cbboyan/solverpy/tree/e1ec665)]
* refactor: update all imports and references from grackle to solverpy_grackle [[details](https://github.com/cbboyan/solverpy/commit/2ff1fbc) | [browse](https://github.com/cbboyan/solverpy/tree/2ff1fbc)]
* refactor: rename grackle package to solverpy_grackle; move learn tests to solverpy-learn [[details](https://github.com/cbboyan/solverpy/commit/71ac712) | [browse](https://github.com/cbboyan/solverpy/tree/71ac712)]
* fix: Runner tests broken by missing Apply plugin simulation [[details](https://github.com/cbboyan/solverpy/commit/064d6bb) | [browse](https://github.com/cbboyan/solverpy/tree/064d6bb)]
* refactor: rename vampire domain classes and remove dead init.py [[details](https://github.com/cbboyan/solverpy/commit/318b04b) | [browse](https://github.com/cbboyan/solverpy/tree/318b04b)]
* refactor: restore bitwuzla domains as DefaultDomain and BitwuzlaDomain [[details](https://github.com/cbboyan/solverpy/commit/a81b922) | [browse](https://github.com/cbboyan/solverpy/tree/a81b922)]
* refactor: remove domain_ prefix from vampire files; rename DefaultDomain to BitwuzlaDomain [[details](https://github.com/cbboyan/solverpy/commit/f9f2eed) | [browse](https://github.com/cbboyan/solverpy/tree/f9f2eed)]
* feat: Annotate domain layer and runner layer; delete dead StageRunner [[details](https://github.com/cbboyan/solverpy/commit/7cf012a) | [browse](https://github.com/cbboyan/solverpy/tree/7cf012a)]
* feat: Add RunnerConfig TypedDict and annotate runner base classes [[details](https://github.com/cbboyan/solverpy/commit/b6b67e0) | [browse](https://github.com/cbboyan/solverpy/tree/b6b67e0)]
* feat: Add Apply plugin to solverpy and wire quality/resources into SolverPyRunner [[details](https://github.com/cbboyan/solverpy/commit/044388c) | [browse](https://github.com/cbboyan/solverpy/tree/044388c)]
* feat: Add RamparilsTrainer and installable entry points for grackle scripts [[details](https://github.com/cbboyan/solverpy/commit/dee1cda) | [browse](https://github.com/cbboyan/solverpy/tree/dee1cda)]

## v2.1.0 (2026-04-10)

* feat!!: Add solverpy-grackle package with full Grackle support [[details](https://github.com/cbboyan/solverpy/commit/2acb53a) | [browse](https://github.com/cbboyan/solverpy/tree/2acb53a)]
* fix: Fix Manager subprocess leak in Talker.log_start() [[details](https://github.com/cbboyan/solverpy/commit/e05b446) | [browse](https://github.com/cbboyan/solverpy/tree/e05b446)]
* fix: Fix file descriptor leak in Outputs.write() [[details](https://github.com/cbboyan/solverpy/commit/52a3c05) | [browse](https://github.com/cbboyan/solverpy/tree/52a3c05)]
* fix: Fix mutable default argument in SolverTask.__init__ [[details](https://github.com/cbboyan/solverpy/commit/7106b62) | [browse](https://github.com/cbboyan/solverpy/tree/7106b62)]
* fix: Remove debug code from launcher.launch() that wrote to ~/debug.log [[details](https://github.com/cbboyan/solverpy/commit/602e85b) | [browse](https://github.com/cbboyan/solverpy/tree/602e85b)]

## v2.0.3 (2026-04-02)

* feat!: Support E Prover new --parse-strategy format via EProverSid plugin. [[details](https://github.com/cbboyan/solverpy/commit/8a8010f) | [browse](https://github.com/cbboyan/solverpy/tree/8a8010f)]

## v2.0.2 (2026-04-02)

* fix!: Fixed ML-looping after package split. [[details](https://github.com/cbboyan/solverpy/commit/4a105a1) | [browse](https://github.com/cbboyan/solverpy/tree/4a105a1)]
* test: testing files [[details](https://github.com/cbboyan/solverpy/commit/055debf) | [browse](https://github.com/cbboyan/solverpy/tree/055debf)]
* test: split SOLVERS into SHELL_SOLVERS/STDIN_SOLVERS fixtures [[details](https://github.com/cbboyan/solverpy/commit/03f52fc) | [browse](https://github.com/cbboyan/solverpy/tree/03f52fc)]

## v2.0.1 (2026-03-25)

* fix!: Fixed comment char in outputs. [[details](https://github.com/cbboyan/solverpy/commit/8423fb0) | [browse](https://github.com/cbboyan/solverpy/tree/8423fb0)]
* feat: Python-native runtime measurement. [[details](https://github.com/cbboyan/solverpy/commit/d6efd86) | [browse](https://github.com/cbboyan/solverpy/tree/d6efd86)]

## v2.0.0 (2026-03-24)

* feat!!!: Major refactor and package split. [[details](https://github.com/cbboyan/solverpy/commit/ec3beb9) | [browse](https://github.com/cbboyan/solverpy/tree/ec3beb9)]
* docs: doc and skills [[details](https://github.com/cbboyan/solverpy/commit/02f7999) | [browse](https://github.com/cbboyan/solverpy/tree/02f7999)]
* docs: documentation pieces [[details](https://github.com/cbboyan/solverpy/commit/d87b0e4) | [browse](https://github.com/cbboyan/solverpy/tree/d87b0e4)]
* refactor: missing type annotations in solverpy [[details](https://github.com/cbboyan/solverpy/commit/960f1e6) | [browse](https://github.com/cbboyan/solverpy/tree/960f1e6)]
* tests: benchmark evaluation tests for cvc5 [[details](https://github.com/cbboyan/solverpy/commit/3fa41ff) | [browse](https://github.com/cbboyan/solverpy/tree/3fa41ff)]
* tests: fix vampire static args [[details](https://github.com/cbboyan/solverpy/commit/0a62d0b) | [browse](https://github.com/cbboyan/solverpy/tree/0a62d0b)]
* refactor: testing of solver runs [[details](https://github.com/cbboyan/solverpy/commit/4674631) | [browse](https://github.com/cbboyan/solverpy/tree/4674631)]
* tests: prover9 and lash inputs [[details](https://github.com/cbboyan/solverpy/commit/de5909b) | [browse](https://github.com/cbboyan/solverpy/tree/de5909b)]
* fix: Fixed search for SZS status [[details](https://github.com/cbboyan/solverpy/commit/9d5742b) | [browse](https://github.com/cbboyan/solverpy/tree/9d5742b)]
* fix: ATP evaluation for Enigma models. [[details](https://github.com/cbboyan/solverpy/commit/2b47e01) | [browse](https://github.com/cbboyan/solverpy/tree/2b47e01)]
* feat: Customize pos/neg weight ration. [[details](https://github.com/cbboyan/solverpy/commit/6279e5a) | [browse](https://github.com/cbboyan/solverpy/tree/6279e5a)]
* fix: Disabling generation of debugging trains. [[details](https://github.com/cbboyan/solverpy/commit/e661db5) | [browse](https://github.com/cbboyan/solverpy/tree/e661db5)]
* feat: Keep pos/neg ratio for cvc5ml. [[details](https://github.com/cbboyan/solverpy/commit/5f8ba0b) | [browse](https://github.com/cbboyan/solverpy/tree/5f8ba0b)]
* feat: Introduce tuning of learning_rate. [[details](https://github.com/cbboyan/solverpy/commit/4850b71) | [browse](https://github.com/cbboyan/solverpy/tree/4850b71)]

## v1.9.2 (2026-01-14)

* fix!: Slow ATP evaluation launching [[details](https://github.com/cbboyan/solverpy/commit/f9ac5a4) | [browse](https://github.com/cbboyan/solverpy/tree/f9ac5a4)]
* feat: Console headless mode and progress bar fixes. [[details](https://github.com/cbboyan/solverpy/commit/b9c03d8) | [browse](https://github.com/cbboyan/solverpy/tree/b9c03d8)]
* feat: ATP evaluation for model building. [[details](https://github.com/cbboyan/solverpy/commit/9a31b55) | [browse](https://github.com/cbboyan/solverpy/tree/9a31b55)]
* feat: Support resource limit for Z3. [[details](https://github.com/cbboyan/solverpy/commit/7ce9b49) | [browse](https://github.com/cbboyan/solverpy/tree/7ce9b49)]
* fix: Evaluation-only runs. [[details](https://github.com/cbboyan/solverpy/commit/1ef62ea) | [browse](https://github.com/cbboyan/solverpy/tree/1ef62ea)]
* docs: Document bids and sids. [[details](https://github.com/cbboyan/solverpy/commit/ed7a823) | [browse](https://github.com/cbboyan/solverpy/tree/ed7a823)]
* docs: Generate svgs for PlantUML just once. [[details](https://github.com/cbboyan/solverpy/commit/3df7fdd) | [browse](https://github.com/cbboyan/solverpy/tree/3df7fdd)]
* docs: Support PlantUML diagrams in the docs. [[details](https://github.com/cbboyan/solverpy/commit/09bd80a) | [browse](https://github.com/cbboyan/solverpy/tree/09bd80a)]
* docs: Documentation schemes. [[details](https://github.com/cbboyan/solverpy/commit/c8e5d06) | [browse](https://github.com/cbboyan/solverpy/tree/c8e5d06)]

## v1.9.1 (2025-09-07)

* fix!: Updated package requirements. [[details](https://github.com/cbboyan/solverpy/commit/bc56e58) | [browse](https://github.com/cbboyan/solverpy/tree/bc56e58)]

## v1.9.0 (2025-09-07)

* feat!!: Major refactor and Enigma tuning features. [[details](https://github.com/cbboyan/solverpy/commit/48c0b30) | [browse](https://github.com/cbboyan/solverpy/tree/48c0b30)]
* fix: Training data linking for MultiTrains. [[details](https://github.com/cbboyan/solverpy/commit/301ac1d) | [browse](https://github.com/cbboyan/solverpy/tree/301ac1d)]
* refactor: Major refactor of setups and evaluation. [[details](https://github.com/cbboyan/solverpy/commit/b5d0ff9) | [browse](https://github.com/cbboyan/solverpy/tree/b5d0ff9)]
* fix: Fixed looping without new trains. [[details](https://github.com/cbboyan/solverpy/commit/b7e7ee2) | [browse](https://github.com/cbboyan/solverpy/tree/b7e7ee2)]
* feat: Implemented call-by-id for plugins. [[details](https://github.com/cbboyan/solverpy/commit/9ee188d) | [browse](https://github.com/cbboyan/solverpy/tree/9ee188d)]
* feat: Filtering of negative samples (forgetting). [[details](https://github.com/cbboyan/solverpy/commit/11262b1) | [browse](https://github.com/cbboyan/solverpy/tree/11262b1)]
* feat: Allow separate tuning params for gen-filter. [[details](https://github.com/cbboyan/solverpy/commit/139cb1a) | [browse](https://github.com/cbboyan/solverpy/tree/139cb1a)]
* fix: Fix memory leaks by running external process. [[details](https://github.com/cbboyan/solverpy/commit/c8e6630) | [browse](https://github.com/cbboyan/solverpy/tree/c8e6630)]
* fix: Fixed model building with `gen` features. [[details](https://github.com/cbboyan/solverpy/commit/6118bdc) | [browse](https://github.com/cbboyan/solverpy/tree/6118bdc)]
* feat: Support of tacticals for Z3 strategies. [[details](https://github.com/cbboyan/solverpy/commit/b14db3d) | [browse](https://github.com/cbboyan/solverpy/tree/b14db3d)]
* refactor: save raw output solver [[details](https://github.com/cbboyan/solverpy/commit/caa8da5) | [browse](https://github.com/cbboyan/solverpy/tree/caa8da5)]
* refactor: Result simulation [[details](https://github.com/cbboyan/solverpy/commit/45fd08c) | [browse](https://github.com/cbboyan/solverpy/tree/45fd08c)]
* refactor: Removed SmtSolver and TptpSolver. [[details](https://github.com/cbboyan/solverpy/commit/d971ef5) | [browse](https://github.com/cbboyan/solverpy/tree/d971ef5)]
* docs: Documentation tools. [[details](https://github.com/cbboyan/solverpy/commit/86142ef) | [browse](https://github.com/cbboyan/solverpy/tree/86142ef)]
* docs: First version of web pages. [[details](https://github.com/cbboyan/solverpy/commit/e7f3244) | [browse](https://github.com/cbboyan/solverpy/tree/e7f3244)]
* feat: Support for Z3 strategies. [[details](https://github.com/cbboyan/solverpy/commit/cfb929c) | [browse](https://github.com/cbboyan/solverpy/tree/cfb929c)]
* fix: Fixed "out of memory" detection for Z3. [[details](https://github.com/cbboyan/solverpy/commit/966ab61) | [browse](https://github.com/cbboyan/solverpy/tree/966ab61)]
* fix: Fixed ulimit memory limit value. [[details](https://github.com/cbboyan/solverpy/commit/a05ca40) | [browse](https://github.com/cbboyan/solverpy/tree/a05ca40)]
* fix: Fixed Z3 memory limit option. [[details](https://github.com/cbboyan/solverpy/commit/1a6eadb) | [browse](https://github.com/cbboyan/solverpy/tree/1a6eadb)]
* fix: Fixed Z3 solver wrapper. [[details](https://github.com/cbboyan/solverpy/commit/d717896) | [browse](https://github.com/cbboyan/solverpy/tree/d717896)]
* refactor: typing and renames [[details](https://github.com/cbboyan/solverpy/commit/8ba1680) | [browse](https://github.com/cbboyan/solverpy/tree/8ba1680)]
* refactor: typing results [[details](https://github.com/cbboyan/solverpy/commit/d581c68) | [browse](https://github.com/cbboyan/solverpy/tree/d581c68)]
* refactor: typing tuners [[details](https://github.com/cbboyan/solverpy/commit/5bd6c1c) | [browse](https://github.com/cbboyan/solverpy/tree/5bd6c1c)]
* refactor: typing various modules [[details](https://github.com/cbboyan/solverpy/commit/b9785b4) | [browse](https://github.com/cbboyan/solverpy/tree/b9785b4)]
* refactor: typing setups [[details](https://github.com/cbboyan/solverpy/commit/4e20305) | [browse](https://github.com/cbboyan/solverpy/tree/4e20305)]
* refactor: typing setups [[details](https://github.com/cbboyan/solverpy/commit/8e92c54) | [browse](https://github.com/cbboyan/solverpy/tree/8e92c54)]
* refactor: typing solvers [[details](https://github.com/cbboyan/solverpy/commit/fa201b3) | [browse](https://github.com/cbboyan/solverpy/tree/fa201b3)]
* refactor: typing solvers [[details](https://github.com/cbboyan/solverpy/commit/e827768) | [browse](https://github.com/cbboyan/solverpy/tree/e827768)]
* refactor: typing plugins [[details](https://github.com/cbboyan/solverpy/commit/007e57b) | [browse](https://github.com/cbboyan/solverpy/tree/007e57b)]
* refactor: typing and renaming [[details](https://github.com/cbboyan/solverpy/commit/4fd1693) | [browse](https://github.com/cbboyan/solverpy/tree/4fd1693)]
* refactor: typing builders [[details](https://github.com/cbboyan/solverpy/commit/553bdad) | [browse](https://github.com/cbboyan/solverpy/tree/553bdad)]
* refactor: typing solvers and providers [[details](https://github.com/cbboyan/solverpy/commit/301b8e9) | [browse](https://github.com/cbboyan/solverpy/tree/301b8e9)]
* feat: Support `delfix` to remove prefix of problem names. [[details](https://github.com/cbboyan/solverpy/commit/c9dda59) | [browse](https://github.com/cbboyan/solverpy/tree/c9dda59)]
* fix: Typo in status provider. [[details](https://github.com/cbboyan/solverpy/commit/fba7102) | [browse](https://github.com/cbboyan/solverpy/tree/fba7102)]
* fix: Add verbosity level for `deconflict` script. [[details](https://github.com/cbboyan/solverpy/commit/d991e59) | [browse](https://github.com/cbboyan/solverpy/tree/d991e59)]
* feat: Tool to remove conflicting pos/neg samples. [[details](https://github.com/cbboyan/solverpy/commit/b04a115) | [browse](https://github.com/cbboyan/solverpy/tree/b04a115)]
* refactor: Make model builder to return booster. [[details](https://github.com/cbboyan/solverpy/commit/960005e) | [browse](https://github.com/cbboyan/solverpy/tree/960005e)]
* feat: Added runtime to the Status plugin. [[details](https://github.com/cbboyan/solverpy/commit/e01d355) | [browse](https://github.com/cbboyan/solverpy/tree/e01d355)]
* feat: Support looping with custum training data. [[details](https://github.com/cbboyan/solverpy/commit/3aea6dd) | [browse](https://github.com/cbboyan/solverpy/tree/3aea6dd)]
* Fix: Repeated ML strategy creation for cvc5. [[details](https://github.com/cbboyan/solverpy/commit/809d2a1) | [browse](https://github.com/cbboyan/solverpy/tree/809d2a1)]
* fix: Correct validation set names in model builder. [[details](https://github.com/cbboyan/solverpy/commit/d2e749e) | [browse](https://github.com/cbboyan/solverpy/tree/d2e749e)]
* refactor: model bulder autotune [[details](https://github.com/cbboyan/solverpy/commit/fee8968) | [browse](https://github.com/cbboyan/solverpy/tree/fee8968)]
* feat: Support early stopping for model training. [[details](https://github.com/cbboyan/solverpy/commit/c68eb65) | [browse](https://github.com/cbboyan/solverpy/tree/c68eb65)]
* feat: Support early stopping for LightGBM. [[details](https://github.com/cbboyan/solverpy/commit/757bb2f) | [browse](https://github.com/cbboyan/solverpy/tree/757bb2f)]
* fix: Fix result update for skipped tasks. [[details](https://github.com/cbboyan/solverpy/commit/31e8655) | [browse](https://github.com/cbboyan/solverpy/tree/31e8655)]
* feat: Restricted evaluation by `solvedby` strategy. [[details](https://github.com/cbboyan/solverpy/commit/1fae006) | [browse](https://github.com/cbboyan/solverpy/tree/1fae006)]
* fix: skip evaluation on trains in the last iter [[details](https://github.com/cbboyan/solverpy/commit/1babecb) | [browse](https://github.com/cbboyan/solverpy/tree/1babecb)]
* fix: Improved TPTP parsing. [[details](https://github.com/cbboyan/solverpy/commit/a2501dc) | [browse](https://github.com/cbboyan/solverpy/tree/a2501dc)]
* fix: Improved TPTP parsing and parents extraction. [[details](https://github.com/cbboyan/solverpy/commit/cffc446) | [browse](https://github.com/cbboyan/solverpy/tree/cffc446)]
* fix: Added antlr4 runtime requirment. [[details](https://github.com/cbboyan/solverpy/commit/0052fd2) | [browse](https://github.com/cbboyan/solverpy/tree/0052fd2)]
* fix: Missing module init of `solverpy.lang`. [[details](https://github.com/cbboyan/solverpy/commit/aa4de97) | [browse](https://github.com/cbboyan/solverpy/tree/aa4de97)]

## v1.8.1 (2024-12-04)

* feat!: Basic TPTP parsering into Python objects. [[details](https://github.com/cbboyan/solverpy/commit/6545648) | [browse](https://github.com/cbboyan/solverpy/tree/6545648)]
* fix: Bitwuzla wrapper timeout and setup. [[details](https://github.com/cbboyan/solverpy/commit/54b140d) | [browse](https://github.com/cbboyan/solverpy/tree/54b140d)]
* fix: Optimized provider commits [[details](https://github.com/cbboyan/solverpy/commit/34eee12) | [browse](https://github.com/cbboyan/solverpy/tree/34eee12)]
* feat: Allow looping from parametric sids. [[details](https://github.com/cbboyan/solverpy/commit/f8c08ab) | [browse](https://github.com/cbboyan/solverpy/tree/f8c08ab)]
* fix: fix type in `weigths` [[details](https://github.com/cbboyan/solverpy/commit/3e19738) | [browse](https://github.com/cbboyan/solverpy/tree/3e19738)]
* fix: Corrected option syntax of solo strategies. [[details](https://github.com/cbboyan/solverpy/commit/d6fad4a) | [browse](https://github.com/cbboyan/solverpy/tree/d6fad4a)]

## v1.8.0 (2024-08-30)

* feat!!: Support for Enigma and cvc5ml models. [[details](https://github.com/cbboyan/solverpy/commit/3fae477) | [browse](https://github.com/cbboyan/solverpy/tree/3fae477)]
* fix: Remove prefer-initial-clauses in Enigmas [[details](https://github.com/cbboyan/solverpy/commit/a5bcded) | [browse](https://github.com/cbboyan/solverpy/tree/a5bcded)]
* fix: Fix tuning with devels and init_params. [[details](https://github.com/cbboyan/solverpy/commit/6c55599) | [browse](https://github.com/cbboyan/solverpy/tree/6c55599)]
* fix: Support training with devels. [[details](https://github.com/cbboyan/solverpy/commit/294c1e8) | [browse](https://github.com/cbboyan/solverpy/tree/294c1e8)]
* fix: Training Enigma sel models without gens. [[details](https://github.com/cbboyan/solverpy/commit/07d023f) | [browse](https://github.com/cbboyan/solverpy/tree/07d023f)]
* feat: Support models for generated filtering. [[details](https://github.com/cbboyan/solverpy/commit/61919ff) | [browse](https://github.com/cbboyan/solverpy/tree/61919ff)]
* refactor: Moved svm and train plugins to builder. [[details](https://github.com/cbboyan/solverpy/commit/2b10896) | [browse](https://github.com/cbboyan/solverpy/tree/2b10896)]
* refactor: Split `benchmark.setups` module. [[details](https://github.com/cbboyan/solverpy/commit/3dbea27) | [browse](https://github.com/cbboyan/solverpy/tree/3dbea27)]
* refactor: Unify solver setups for evaluation. [[details](https://github.com/cbboyan/solverpy/commit/9f6b502) | [browse](https://github.com/cbboyan/solverpy/tree/9f6b502)]
* feature: Model builder for cvc5. [[details](https://github.com/cbboyan/solverpy/commit/9ff94be) | [browse](https://github.com/cbboyan/solverpy/tree/9ff94be)]
* feat: Show trial statistics in autotune. [[details](https://github.com/cbboyan/solverpy/commit/9bc9999) | [browse](https://github.com/cbboyan/solverpy/tree/9bc9999)]
* feat: Model pretty tuner with progress bars [[details](https://github.com/cbboyan/solverpy/commit/ee35eef) | [browse](https://github.com/cbboyan/solverpy/tree/ee35eef)]
* feat: Added ouput redirecting tools. [[details](https://github.com/cbboyan/solverpy/commit/19faa95) | [browse](https://github.com/cbboyan/solverpy/tree/19faa95)]
* fix: Updated Python package requirements. [[details](https://github.com/cbboyan/solverpy/commit/19c25c9) | [browse](https://github.com/cbboyan/solverpy/tree/19c25c9)]
* feat: Hyperparameter tuner for LightGBM. [[details](https://github.com/cbboyan/solverpy/commit/fb21718) | [browse](https://github.com/cbboyan/solverpy/tree/fb21718)]
* fix: Directory creation for debug train files [[details](https://github.com/cbboyan/solverpy/commit/ec4249b) | [browse](https://github.com/cbboyan/solverpy/tree/ec4249b)]
* fix: Use features inside train paths [[details](https://github.com/cbboyan/solverpy/commit/2e6d83a) | [browse](https://github.com/cbboyan/solverpy/tree/2e6d83a)]
* feat: Trains debugging mode for ENIGMA [[details](https://github.com/cbboyan/solverpy/commit/4167a2a) | [browse](https://github.com/cbboyan/solverpy/tree/4167a2a)]
* feat: Trains extractor for ENIGMA [[details](https://github.com/cbboyan/solverpy/commit/8f7ca16) | [browse](https://github.com/cbboyan/solverpy/tree/8f7ca16)]
* feat: Use git hooks from git-auto-version. [[details](https://github.com/cbboyan/solverpy/commit/e7f908e) | [browse](https://github.com/cbboyan/solverpy/tree/e7f908e)]

## v1.7.1 (2024-08-09)

* feat!: use git hooks for auto versioning [[details](https://github.com/cbboyan/solverpy/commit/9be96cd) | [browse](https://github.com/cbboyan/solverpy/tree/9be96cd)]
* docs: Update options.md [[details](https://github.com/cbboyan/solverpy/commit/249e817) | [browse](https://github.com/cbboyan/solverpy/tree/249e817)]
* docs: added example archive [[details](https://github.com/cbboyan/solverpy/commit/6c9ba77) | [browse](https://github.com/cbboyan/solverpy/tree/6c9ba77)]

## v1.7.0 (2024-07-31)

* feat: pip compatible version [[details](https://github.com/cbboyan/solverpy/commit/2a38843) | [browse](https://github.com/cbboyan/solverpy/tree/2a38843)]
* fix: allow restarts [[details](https://github.com/cbboyan/solverpy/commit/edbd7a5) | [browse](https://github.com/cbboyan/solverpy/tree/edbd7a5)]

## v1.6.15 (2024-04-12)

* fix: correct reporting status for timed out runs [[details](https://github.com/cbboyan/solverpy/commit/b62e727) | [browse](https://github.com/cbboyan/solverpy/tree/b62e727)]
* doc: first pieces of documentation [[details](https://github.com/cbboyan/solverpy/commit/905012e) | [browse](https://github.com/cbboyan/solverpy/tree/905012e)]
* docs: Update options.md [[details](https://github.com/cbboyan/solverpy/commit/e764abe) | [browse](https://github.com/cbboyan/solverpy/tree/e764abe)]
* docs: Update options.md [[details](https://github.com/cbboyan/solverpy/commit/d832562) | [browse](https://github.com/cbboyan/solverpy/tree/d832562)]
* docs: option description [[details](https://github.com/cbboyan/solverpy/commit/182c776) | [browse](https://github.com/cbboyan/solverpy/tree/182c776)]

## v1.6.14 (2024-03-16)

* fix: keep compressed data after decompress [[details](https://github.com/cbboyan/solverpy/commit/2071e1a) | [browse](https://github.com/cbboyan/solverpy/tree/2071e1a)]

## v1.6.13 (2024-03-14)

* fix: skip building existing models [[details](https://github.com/cbboyan/solverpy/commit/820a29b) | [browse](https://github.com/cbboyan/solverpy/tree/820a29b)]

## v1.6.12 (2024-03-14)

* fix: status handling in markdown.py [[details](https://github.com/cbboyan/solverpy/commit/85e470b) | [browse](https://github.com/cbboyan/solverpy/tree/85e470b)]

## v1.6.11 (2024-03-14)

* fix: mardown output for failed results [[details](https://github.com/cbboyan/solverpy/commit/44c91a7) | [browse](https://github.com/cbboyan/solverpy/tree/44c91a7)]
* data: cvc5 strategies from smt-comp [[details](https://github.com/cbboyan/solverpy/commit/f83707e) | [browse](https://github.com/cbboyan/solverpy/tree/f83707e)]

## v1.6.10 (2024-03-03)

* fix: set by default the -Lsmt2 flag for cvc5 [[details](https://github.com/cbboyan/solverpy/commit/2f799e4) | [browse](https://github.com/cbboyan/solverpy/tree/2f799e4)]

## v1.6.9 (2024-02-13)

* fix: recompute GaveUp's and add memory limit 2GB [[details](https://github.com/cbboyan/solverpy/commit/7cf17bc) | [browse](https://github.com/cbboyan/solverpy/tree/7cf17bc)]

## v1.6.8 (2024-01-29)

* fix: detect Prover9 termination reasons [[details](https://github.com/cbboyan/solverpy/commit/b47c645) | [browse](https://github.com/cbboyan/solverpy/tree/b47c645)]

## v1.6.7 (2024-01-28)

* fix: check timeout exitcode and set Timeout status [[details](https://github.com/cbboyan/solverpy/commit/e3fe48c) | [browse](https://github.com/cbboyan/solverpy/tree/e3fe48c)]

## v1.6.6 (2024-01-28)

* fix: make Prover9 incomplete by default [[details](https://github.com/cbboyan/solverpy/commit/5b04abc) | [browse](https://github.com/cbboyan/solverpy/tree/5b04abc)]

## v1.6.5 (2024-01-27)

* fix: ensure prover9 terminates [[details](https://github.com/cbboyan/solverpy/commit/f3b6c92) | [browse](https://github.com/cbboyan/solverpy/tree/f3b6c92)]

## v1.6.4 (2024-01-26)

* fix: do not print command in StdinSolver [[details](https://github.com/cbboyan/solverpy/commit/93c3da0) | [browse](https://github.com/cbboyan/solverpy/tree/93c3da0)]

## v1.6.3 (2024-01-26)

* fix: prover9 solver setup [[details](https://github.com/cbboyan/solverpy/commit/6c6c48c) | [browse](https://github.com/cbboyan/solverpy/tree/6c6c48c)]

## v1.6.2 (2024-01-26)

* fix: change prover9 static options [[details](https://github.com/cbboyan/solverpy/commit/d11cb0c) | [browse](https://github.com/cbboyan/solverpy/tree/d11cb0c)]

## v1.6.1 (2024-01-24)

* fix: setup for a general solver [[details](https://github.com/cbboyan/solverpy/commit/8550265) | [browse](https://github.com/cbboyan/solverpy/tree/8550265)]

## v1.6.0 (2024-01-22)

* feat: ATP wrapper for Prover9 [[details](https://github.com/cbboyan/solverpy/commit/59da0f8) | [browse](https://github.com/cbboyan/solverpy/tree/59da0f8)]

## v1.5.0 (2024-01-17)

* feat: basic ntfy support [[details](https://github.com/cbboyan/solverpy/commit/8da18e4) | [browse](https://github.com/cbboyan/solverpy/tree/8da18e4)]

## v1.4.1 (2024-01-13)

* fix: timed solver repr string fix [[details](https://github.com/cbboyan/solverpy/commit/2d46bca) | [browse](https://github.com/cbboyan/solverpy/tree/2d46bca)]

## v1.4.0 (2023-11-09)

* feat: support cvc5 as an atp/tptp solver [[details](https://github.com/cbboyan/solverpy/commit/42d6b47) | [browse](https://github.com/cbboyan/solverpy/tree/42d6b47)]

## v1.3.5 (2023-09-03)

* fix: set OMP_NUM_THREADS=1 for shell solvers [[details](https://github.com/cbboyan/solverpy/commit/41e8ffa) | [browse](https://github.com/cbboyan/solverpy/tree/41e8ffa)]

## v1.3.4 (2023-09-03)

* fix: skip merging train in the last loop [[details](https://github.com/cbboyan/solverpy/commit/a011368) | [browse](https://github.com/cbboyan/solverpy/tree/a011368)]

## v1.3.3 (2023-09-03)

* fix: skip building model in the last loop [[details](https://github.com/cbboyan/solverpy/commit/1a48852) | [browse](https://github.com/cbboyan/solverpy/tree/1a48852)]

## v1.3.2 (2023-09-01)

* fix: support for looping with development set [[details](https://github.com/cbboyan/solverpy/commit/5609d20) | [browse](https://github.com/cbboyan/solverpy/tree/5609d20)]

## v1.3.1 (2023-09-01)

* fix: support multiple evalution loops [[details](https://github.com/cbboyan/solverpy/commit/c1bf301) | [browse](https://github.com/cbboyan/solverpy/tree/c1bf301)]

## v1.3.0 (2023-09-01)

* feat: support for merging of trains [[details](https://github.com/cbboyan/solverpy/commit/c2ae164) | [browse](https://github.com/cbboyan/solverpy/tree/c2ae164)]

## v1.2.1 (2023-08-30)

* fix: setup for cvc5 model builder [[details](https://github.com/cbboyan/solverpy/commit/5f101c3) | [browse](https://github.com/cbboyan/solverpy/tree/5f101c3)]
* build: update version control [[details](https://github.com/cbboyan/solverpy/commit/ad9ed7f) | [browse](https://github.com/cbboyan/solverpy/tree/ad9ed7f)]
* build: auto update of git version tags [[details](https://github.com/cbboyan/solverpy/commit/550c3f1) | [browse](https://github.com/cbboyan/solverpy/tree/550c3f1)]

## v1.2.0 (2023-08-29)

* feat: introduce model builders for lgbtune [[details](https://github.com/cbboyan/solverpy/commit/a40d6a3) | [browse](https://github.com/cbboyan/solverpy/tree/a40d6a3)]

## v1.1.0 (2023-08-25)

* feat: add debug-trains option [[details](https://github.com/cbboyan/solverpy/commit/0b6ee06) | [browse](https://github.com/cbboyan/solverpy/tree/0b6ee06)]

## v1.0.0 (2023-08-24)

* setup scripts [[details](https://github.com/cbboyan/solverpy/commit/6c1123e) | [browse](https://github.com/cbboyan/solverpy/tree/6c1123e)]
* common setup initializers [[details](https://github.com/cbboyan/solverpy/commit/8457760) | [browse](https://github.com/cbboyan/solverpy/tree/8457760)]
* solver limits & compress jsons [[details](https://github.com/cbboyan/solverpy/commit/567b3b0) | [browse](https://github.com/cbboyan/solverpy/tree/567b3b0)]
* limit comparison methods [[details](https://github.com/cbboyan/solverpy/commit/5cb096f) | [browse](https://github.com/cbboyan/solverpy/tree/5cb096f)]
* allow forced evaluation [[details](https://github.com/cbboyan/solverpy/commit/5b1630a) | [browse](https://github.com/cbboyan/solverpy/tree/5b1630a)]
* shuffle tasks [[details](https://github.com/cbboyan/solverpy/commit/cfb3d70) | [browse](https://github.com/cbboyan/solverpy/tree/cfb3d70)]
* deps [[details](https://github.com/cbboyan/solverpy/commit/4072af7) | [browse](https://github.com/cbboyan/solverpy/tree/4072af7)]
* improve progress bar time estimate [[details](https://github.com/cbboyan/solverpy/commit/567fa77) | [browse](https://github.com/cbboyan/solverpy/tree/567fa77)]
* allow uncompressed [[details](https://github.com/cbboyan/solverpy/commit/4fb79c3) | [browse](https://github.com/cbboyan/solverpy/tree/4fb79c3)]
* gzip outputs  & flatten is default [[details](https://github.com/cbboyan/solverpy/commit/073b593) | [browse](https://github.com/cbboyan/solverpy/tree/073b593)]
* fix default mem limit [[details](https://github.com/cbboyan/solverpy/commit/0a82b4e) | [browse](https://github.com/cbboyan/solverpy/tree/0a82b4e)]
* default memory limit to 4GB [[details](https://github.com/cbboyan/solverpy/commit/3fb6c11) | [browse](https://github.com/cbboyan/solverpy/tree/3fb6c11)]
* default memory limit to 2GB [[details](https://github.com/cbboyan/solverpy/commit/1543126) | [browse](https://github.com/cbboyan/solverpy/tree/1543126)]
* memory limit plugin [[details](https://github.com/cbboyan/solverpy/commit/96eb79d) | [browse](https://github.com/cbboyan/solverpy/tree/96eb79d)]
* simplify legend [[details](https://github.com/cbboyan/solverpy/commit/ced62df) | [browse](https://github.com/cbboyan/solverpy/tree/ced62df)]
* missing file [[details](https://github.com/cbboyan/solverpy/commit/065244b) | [browse](https://github.com/cbboyan/solverpy/tree/065244b)]
* compress scripts [[details](https://github.com/cbboyan/solverpy/commit/77968e7) | [browse](https://github.com/cbboyan/solverpy/tree/77968e7)]
* logging compressing [[details](https://github.com/cbboyan/solverpy/commit/0134ea4) | [browse](https://github.com/cbboyan/solverpy/tree/0134ea4)]
* svm trains basic functions [[details](https://github.com/cbboyan/solverpy/commit/4be3032) | [browse](https://github.com/cbboyan/solverpy/tree/4be3032)]
* improve progress bar report [[details](https://github.com/cbboyan/solverpy/commit/c4c8bb8) | [browse](https://github.com/cbboyan/solverpy/tree/c4c8bb8)]
* extract cvc5 training samples [[details](https://github.com/cbboyan/solverpy/commit/1ae1b2e) | [browse](https://github.com/cbboyan/solverpy/tree/1ae1b2e)]
* loader provider [[details](https://github.com/cbboyan/solverpy/commit/960dbe6) | [browse](https://github.com/cbboyan/solverpy/tree/960dbe6)]
* database commit fixed [[details](https://github.com/cbboyan/solverpy/commit/d90052e) | [browse](https://github.com/cbboyan/solverpy/tree/d90052e)]
* storing of announced cached results [[details](https://github.com/cbboyan/solverpy/commit/d2c6902) | [browse](https://github.com/cbboyan/solverpy/tree/d2c6902)]
* remove debug print [[details](https://github.com/cbboyan/solverpy/commit/b99e6df) | [browse](https://github.com/cbboyan/solverpy/tree/b99e6df)]
* import bids [[details](https://github.com/cbboyan/solverpy/commit/99fae59) | [browse](https://github.com/cbboyan/solverpy/tree/99fae59)]
* db restructure and replace slashes in sid names [[details](https://github.com/cbboyan/solverpy/commit/d22b044) | [browse](https://github.com/cbboyan/solverpy/tree/d22b044)]
* repr for plugins [[details](https://github.com/cbboyan/solverpy/commit/6791886) | [browse](https://github.com/cbboyan/solverpy/tree/6791886)]
* reloader solver [[details](https://github.com/cbboyan/solverpy/commit/2e9a2c2) | [browse](https://github.com/cbboyan/solverpy/tree/2e9a2c2)]
* gitignore update [[details](https://github.com/cbboyan/solverpy/commit/0c4fd64) | [browse](https://github.com/cbboyan/solverpy/tree/0c4fd64)]
* trains plugin; file path flattening [[details](https://github.com/cbboyan/solverpy/commit/a876ed7) | [browse](https://github.com/cbboyan/solverpy/tree/a876ed7)]
* compute par2 score [[details](https://github.com/cbboyan/solverpy/commit/16e10a8) | [browse](https://github.com/cbboyan/solverpy/tree/16e10a8)]
* setup report [[details](https://github.com/cbboyan/solverpy/commit/c2c7396) | [browse](https://github.com/cbboyan/solverpy/tree/c2c7396)]
* statuses report [[details](https://github.com/cbboyan/solverpy/commit/5790c1e) | [browse](https://github.com/cbboyan/solverpy/tree/5790c1e)]
* refactor providers [[details](https://github.com/cbboyan/solverpy/commit/3967a3f) | [browse](https://github.com/cbboyan/solverpy/tree/3967a3f)]
* solved and status providers [[details](https://github.com/cbboyan/solverpy/commit/dffc17c) | [browse](https://github.com/cbboyan/solverpy/tree/dffc17c)]
* default db [[details](https://github.com/cbboyan/solverpy/commit/e2ec7e1) | [browse](https://github.com/cbboyan/solverpy/tree/e2ec7e1)]
* launcher init [[details](https://github.com/cbboyan/solverpy/commit/e407e0c) | [browse](https://github.com/cbboyan/solverpy/tree/e407e0c)]
* improve bar message [[details](https://github.com/cbboyan/solverpy/commit/89d8a98) | [browse](https://github.com/cbboyan/solverpy/tree/89d8a98)]
* markdown legend and summary [[details](https://github.com/cbboyan/solverpy/commit/642e0ff) | [browse](https://github.com/cbboyan/solverpy/tree/642e0ff)]
* refactor timeouts and limits [[details](https://github.com/cbboyan/solverpy/commit/8c8c62f) | [browse](https://github.com/cbboyan/solverpy/tree/8c8c62f)]
* timedsolver refactor [[details](https://github.com/cbboyan/solverpy/commit/8284ef9) | [browse](https://github.com/cbboyan/solverpy/tree/8284ef9)]
* added TimedSolver [[details](https://github.com/cbboyan/solverpy/commit/ee3b672) | [browse](https://github.com/cbboyan/solverpy/tree/ee3b672)]
* remove old code [[details](https://github.com/cbboyan/solverpy/commit/9f2e4f0) | [browse](https://github.com/cbboyan/solverpy/tree/9f2e4f0)]

## v0.1.1 (2023-05-15)

* gitignore [[details](https://github.com/cbboyan/solverpy/commit/9dae105) | [browse](https://github.com/cbboyan/solverpy/tree/9dae105)]
* auto versioning with setuptools-git-versioning [[details](https://github.com/cbboyan/solverpy/commit/1824d2e) | [browse](https://github.com/cbboyan/solverpy/tree/1824d2e)]
* db refactor [[details](https://github.com/cbboyan/solverpy/commit/7528ffa) | [browse](https://github.com/cbboyan/solverpy/tree/7528ffa)]
* remove yamls from dbdebug [[details](https://github.com/cbboyan/solverpy/commit/24cd468) | [browse](https://github.com/cbboyan/solverpy/tree/24cd468)]
* fix unspacing [[details](https://github.com/cbboyan/solverpy/commit/0e00966) | [browse](https://github.com/cbboyan/solverpy/tree/0e00966)]
* add unspace to ShellSolver [[details](https://github.com/cbboyan/solverpy/commit/82a56cf) | [browse](https://github.com/cbboyan/solverpy/tree/82a56cf)]
* remove unspacing from sid [[details](https://github.com/cbboyan/solverpy/commit/42649bd) | [browse](https://github.com/cbboyan/solverpy/tree/42649bd)]
* parametric sids [[details](https://github.com/cbboyan/solverpy/commit/0c2be10) | [browse](https://github.com/cbboyan/solverpy/tree/0c2be10)]
* refactor paths [[details](https://github.com/cbboyan/solverpy/commit/287e144) | [browse](https://github.com/cbboyan/solverpy/tree/287e144)]
* default plugins [[details](https://github.com/cbboyan/solverpy/commit/81d153a) | [browse](https://github.com/cbboyan/solverpy/tree/81d153a)]
* simplify db plugins [[details](https://github.com/cbboyan/solverpy/commit/43ed840) | [browse](https://github.com/cbboyan/solverpy/tree/43ed840)]
* cvc5 fixes and multiple evaluation [[details](https://github.com/cbboyan/solverpy/commit/d1cc0fe) | [browse](https://github.com/cbboyan/solverpy/tree/d1cc0fe)]
* flushing of provider plugins [[details](https://github.com/cbboyan/solverpy/commit/2bd23ed) | [browse](https://github.com/cbboyan/solverpy/tree/2bd23ed)]
* structure modules [[details](https://github.com/cbboyan/solverpy/commit/badce54) | [browse](https://github.com/cbboyan/solverpy/tree/badce54)]
* init version [[details](https://github.com/cbboyan/solverpy/commit/add802e) | [browse](https://github.com/cbboyan/solverpy/tree/add802e)]

## v0.0.0 (2023-04-24)

* Initial commit [[details](https://github.com/cbboyan/solverpy/commit/fdb12ea) | [browse](https://github.com/cbboyan/solverpy/tree/fdb12ea)]

