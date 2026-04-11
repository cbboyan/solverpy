#!/usr/bin/env python3
"""
Convert eprover --print-strategy output to equivalent CLI arguments.

Usage:
  eprover-ho --print-strategy=NAME | python3 strategy2args.py
  python3 strategy2args.py <(eprover-ho --print-strategy=NAME)
  python3 strategy2args.py strategy.txt
"""

import sys
import re

# Sentinel values
LLONG_MAX = 9223372036854775807
LLONG_MIN = -9223372036854775808

# Defaults from source
DEFAULTS_ORDER = {
    'ordertype':               'KBO6',
    'to_weight_gen':           'none',
    'to_prec_gen':             'none',
    'rewrite_strong_rhs_inst': False,
    'to_pre_prec':             '',
    'conj_only_mod':           0,
    'conj_axiom_mod':          0,
    'axiom_only_mod':          0,
    'skolem_mod':              0,
    'defpred_mod':             0,
    'force_kbo_var_weight':    False,   # no CLI option
    'to_pre_weights':          '',
    'to_const_weight':         0,       # WConstNoWeight
    'to_defs_min':             False,   # no CLI option
    'lit_cmp':                 1,       # LCNormal
    'lam_w':                   20,
    'db_w':                    10,
    'ho_order_kind':           'lfho',
}

DEFAULTS_MAIN = {
    'no_preproc':                    False,
    'eqdef_maxclauses':              20000,
    'eqdef_incrlimit':               20,
    'formula_def_limit':             24,
    'miniscope_limit':               1048576,
    'sine':                          'None',
    'add_goal_defs_pos':             False,
    'add_goal_defs_neg':             False,
    'add_goal_defs_subterms':        False,
    'heuristic_name':                'Default',
    'heuristic_def':                 '',
    'prefer_initial_clauses':        False,
    'selection_strategy':            'SelectNoLiterals',
    'pos_lit_sel_min':               0,
    'pos_lit_sel_max':               LLONG_MAX,
    'neg_lit_sel_min':               0,
    'neg_lit_sel_max':               LLONG_MAX,
    'all_lit_sel_min':               0,
    'all_lit_sel_max':               LLONG_MAX,
    'weight_sel_min':                0,
    'select_on_proc_only':           False,
    'inherit_paramod_lit':           False,
    'inherit_goal_pm_lit':           False,
    'inherit_conj_pm_lit':           False,
    'enable_eq_factoring':           True,
    'enable_neg_unit_paramod':       True,
    'enable_given_forward_simpl':    True,
    'pm_type':                       'ParamodPlain',
    'ac_handling':                   1,     # ACDiscardAll
    'ac_res_aggressive':             True,
    'forward_context_sr':            False,
    'forward_context_sr_aggressive': False,
    'backward_context_sr':           False,
    'forward_subsumption_aggressive':False,
    'forward_demod':                 2,     # FullRewrite
    'prefer_general':                False,
    'condensing':                    False,
    'condensing_aggressive':         False,
    'er_varlit_destructive':         False,
    'er_strong_destructive':         False,
    'er_aggressive':                 False,
    'split_clauses':                 0,
    'split_method':                  0,
    'split_aggressive':              False,
    'split_fresh_defs':              True,
    'diseq_decomposition':           0,
    'diseq_decomp_maxarity':         LLONG_MAX,
    'rw_bw_index_type':              'FP7',
    'pm_from_index_type':            'FP7',
    'pm_into_index_type':            'FP7',
    'sat_check_grounding':           'NoGrounding',
    'sat_check_step_limit':          LLONG_MAX,
    'sat_check_size_limit':          LLONG_MAX,
    'sat_check_ttinsert_limit':      LLONG_MAX,
    'sat_check_normconst':           False,
    'sat_check_normalize':           False,
    'sat_check_decision_limit':      10000,
    'filter_orphans_limit':          LLONG_MAX,
    'forward_contract_limit':        LLONG_MAX,
    'delete_bad_limit':              LLONG_MAX,
    'mem_limit':                     0,
    'watchlist_simplify':            True,
    'watchlist_is_static':           False,  # no direct CLI bool option
    'use_tptp_sos':                  False,
    'presat_interreduction':         False,
    'detsort_bw_rw':                 False,
    'detsort_tmpset':                False,
    'arg_cong':                      'all',  # AllLits
    'neg_ext':                       'off',  # NoLits
    'pos_ext':                       'off',  # NoLits
    'ext_rules_max_depth':           -1,  # NO_EXT_SUP
    'inverse_recognition':           False,
    'replace_inj_defs':              False,
    'lift_lambdas':                  True,
    'lambda_to_forall':              True,
    'unroll_only_formulas':          True,
    'elim_leibniz_max_depth':        -1,
    'prim_enum_mode':                'pragmatic',
    'prim_enum_max_depth':           -1,
    'inst_choice_max_depth':         -1,
    'local_rw':                      False,
    'prune_args':                    False,
    'preinstantiate_induction':      False,
    'fool_unroll':                   True,
    'func_proj_limit':               0,
    'imit_limit':                    0,
    'ident_limit':                   0,
    'elim_limit':                    0,
    'unif_mode':                     'single',
    'pattern_oracle':                True,
    'fixpoint_oracle':               True,
    'max_unifiers':                  4,
    'max_unif_steps':                256,
}

# Fields that exist in --print-strategy but have no CLI equivalent
NO_CLI_OPTION = {'force_kbo_var_weight', 'to_defs_min', 'watchlist_is_static'}


def parse_bool(s):
    return s.lower() in ('true', '1', 'yes')

def parse_str(s):
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s

def parse_val(s):
    """Parse a strategy value as int, bool, or string."""
    s = s.strip()
    if s.lower() in ('true', 'false'):
        return parse_bool(s)
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    try:
        return int(s)
    except ValueError:
        return s

def parse_strategy(text):
    """Parse --print-strategy output into (order_params, main_params) dicts."""
    order = {}
    main = {}

    lines = text.splitlines()
    depth = 0        # nesting depth of { }
    in_order = False # currently inside the inner { } (ordering block)

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith('%'):
            continue
        opens  = line.count('{')
        closes = line.count('}')
        was_depth = depth
        depth += opens - closes

        # A line like "   {" at depth 0→1 is the outer block open
        # A line like "   {" at depth 1→2 is the ordering block open
        if opens and not closes:
            if was_depth == 1:
                in_order = True
            continue
        if closes and not opens:
            if in_order and was_depth == 2:
                in_order = False
            continue

        m = re.match(r'(\w+)\s*:\s*(.*)', line)
        if m:
            key = m.group(1)
            val = parse_val(m.group(2).rstrip())
            if in_order:
                order[key] = val
            elif depth >= 1:
                main[key] = val

    return order, main


def strategy_to_args(text, no_sine=False):
    order, main = parse_strategy(text)
    args = []
    heuristic_arg = []
    warnings = []

    def emit(arg):
        args.append(arg)

    def flag(arg, val, default):
        if val != default:
            args.append(arg)

    def fmt(val):
        if isinstance(val, bool):
            return 'true' if val else 'false'
        return val

    def opt(name, val, default=None):
        if default is None or val != default:
            args.append(f'--{name}={fmt(val)}')

    def warn(msg):
        warnings.append(f'# WARNING: {msg}')

    # ── Ordering params ────────────────────────────────────────────────

    ot = order.get('ordertype', DEFAULTS_ORDER['ordertype'])
    emit(f'-t{ot}')

    wg = order.get('to_weight_gen', DEFAULTS_ORDER['to_weight_gen'])
    opt('order-weight-generation', wg, DEFAULTS_ORDER['to_weight_gen'])

    pg = order.get('to_prec_gen', DEFAULTS_ORDER['to_prec_gen'])
    opt('order-precedence-generation', pg, DEFAULTS_ORDER['to_prec_gen'])

    if order.get('rewrite_strong_rhs_inst', DEFAULTS_ORDER['rewrite_strong_rhs_inst']):
        emit('--strong-rw-inst')

    prec = order.get('to_pre_prec', DEFAULTS_ORDER['to_pre_prec'])
    if prec:
        emit(f'--precedence={prec}')

    opt('prec-pure-conj',  order.get('conj_only_mod',  0), 0)
    opt('prec-conj-axiom', order.get('conj_axiom_mod', 0), 0)
    opt('prec-pure-axiom', order.get('axiom_only_mod', 0), 0)
    opt('prec-skolem',     order.get('skolem_mod',     0), 0)
    opt('prec-defpred',    order.get('defpred_mod',    0), 0)

    pw = order.get('to_pre_weights', DEFAULTS_ORDER['to_pre_weights'])
    if pw:
        emit(f'--order-weights={pw}')

    cw = order.get('to_const_weight', DEFAULTS_ORDER['to_const_weight'])
    opt('order-constant-weight', cw, DEFAULTS_ORDER['to_const_weight'])

    # lit_cmp: 0=None, 1=Normal(default), 2=TFOEqMax, 3=TFOEqMin
    lit_cmp = order.get('lit_cmp', DEFAULTS_ORDER['lit_cmp'])
    lit_cmp_names = {0: 'None', 1: 'Normal', 2: 'TFOEqMax', 3: 'TFOEqMin'}
    if lit_cmp != DEFAULTS_ORDER['lit_cmp']:
        emit(f'--literal-comparison={lit_cmp_names.get(lit_cmp, str(lit_cmp))}')

    lam_w = order.get('lam_w', DEFAULTS_ORDER['lam_w'])
    opt('kbo-lam-weight', lam_w, DEFAULTS_ORDER['lam_w'])

    db_w = order.get('db_w', DEFAULTS_ORDER['db_w'])
    opt('kbo-db-weight', db_w, DEFAULTS_ORDER['db_w'])

    hok = order.get('ho_order_kind', DEFAULTS_ORDER['ho_order_kind'])
    opt('ho-order-kind', hok, DEFAULTS_ORDER['ho_order_kind'])

    for field in ('force_kbo_var_weight', 'to_defs_min'):
        val = order.get(field, DEFAULTS_ORDER[field])
        if val != DEFAULTS_ORDER[field]:
            warn(f'{field}={val!r} has no CLI equivalent (use --parse-strategy)')

    # ── Preprocessing ─────────────────────────────────────────────────

    if main.get('no_preproc', False):
        emit('--no-preprocessing')

    eqdef_max = main.get('eqdef_maxclauses', DEFAULTS_MAIN['eqdef_maxclauses'])
    opt('eq-unfold-maxclauses', eqdef_max, DEFAULTS_MAIN['eqdef_maxclauses'])

    eqdef_incr = main.get('eqdef_incrlimit', DEFAULTS_MAIN['eqdef_incrlimit'])
    if eqdef_incr == LLONG_MIN:
        emit('--no-eq-unfolding')
    else:
        opt('eq-unfold-limit', eqdef_incr, DEFAULTS_MAIN['eqdef_incrlimit'])

    fdl = main.get('formula_def_limit', DEFAULTS_MAIN['formula_def_limit'])
    opt('definitional-cnf', fdl, DEFAULTS_MAIN['formula_def_limit'])

    ml = main.get('miniscope_limit', DEFAULTS_MAIN['miniscope_limit'])
    opt('miniscope-limit', ml, DEFAULTS_MAIN['miniscope_limit'])

    sine = main.get('sine', DEFAULTS_MAIN['sine'])
    if not no_sine and sine and sine != 'None':
        emit(f"--sine='{sine}'")

    pos = main.get('add_goal_defs_pos', False)
    neg = main.get('add_goal_defs_neg', False)
    if pos and neg:
        emit('--goal-defs=All')
    elif neg:
        emit('--goal-defs=Neg')

    if main.get('add_goal_defs_subterms', False):
        emit('--goal-subterm-defs')

    if main.get('presat_interreduction', False):
        emit('--presat-simplify')

    # ── Heuristic ─────────────────────────────────────────────────────

    hname = main.get('heuristic_name', DEFAULTS_MAIN['heuristic_name'])
    hdef  = main.get('heuristic_def',  DEFAULTS_MAIN['heuristic_def'])

    if hdef:
        hdef = re.sub(r'(\d)\.([A-Za-z])', r'\1*\2', hdef)
        if hname == 'Default':
            # Passing just (def) makes it the "Default" heuristic
            heuristic_arg.append(f"-H'{hdef}'")
        else:
            emit(f'-x{hname}')
            heuristic_arg.append(f"-H'{hname}={hdef}'")
    elif hname != DEFAULTS_MAIN['heuristic_name']:
        emit(f'-x{hname}')

    if main.get('prefer_initial_clauses', False):
        emit('--prefer-initial-clauses')

    # ── Literal selection ─────────────────────────────────────────────

    sel = main.get('selection_strategy', DEFAULTS_MAIN['selection_strategy'])
    opt('literal-selection-strategy', sel, DEFAULTS_MAIN['selection_strategy'])

    opt('selection-pos-min', main.get('pos_lit_sel_min', 0), 0)
    if main.get('pos_lit_sel_max', LLONG_MAX) != LLONG_MAX:
        emit(f"--selection-pos-max={main['pos_lit_sel_max']}")
    opt('selection-neg-min', main.get('neg_lit_sel_min', 0), 0)
    if main.get('neg_lit_sel_max', LLONG_MAX) != LLONG_MAX:
        emit(f"--selection-neg-max={main['neg_lit_sel_max']}")
    opt('selection-all-min', main.get('all_lit_sel_min', 0), 0)
    if main.get('all_lit_sel_max', LLONG_MAX) != LLONG_MAX:
        emit(f"--selection-all-max={main['all_lit_sel_max']}")
    opt('selection-weight-min', main.get('weight_sel_min', 0), 0)

    if main.get('select_on_proc_only', False):
        emit('--select-on-processing-only')
    if main.get('inherit_paramod_lit', False):
        emit('--inherit-paramod-literals')
    if main.get('inherit_goal_pm_lit', False):
        emit('--inherit-goal-pm-literals')
    if main.get('inherit_conj_pm_lit', False):
        emit('--inherit-conjecture-pm-literals')

    # ── Inference control ─────────────────────────────────────────────

    if not main.get('enable_eq_factoring', True):
        emit('--disable-eq-factoring')
    if not main.get('enable_neg_unit_paramod', True):
        emit('--disable-paramod-into-neg-units')
    if not main.get('enable_given_forward_simpl', True):
        emit('--disable-given-clause-fw-contraction')

    pm = main.get('pm_type', DEFAULTS_MAIN['pm_type'])
    pm_flags = {
        'ParamodSim':             '--simul-paramod',
        'ParamodOrientedSim':     '--oriented-simul-paramod',
        'ParamodSuperSim':        '--supersimul-paramod',
        'ParamodOrientedSuperSim':'--oriented-supersimul-paramod',
    }
    if pm in pm_flags:
        emit(pm_flags[pm])

    # ── AC handling ───────────────────────────────────────────────────

    # 0=NoACHandling, 1=ACDiscardAll(default), 2=ACKeepUnits, 3=ACKeepOrientable
    ac = main.get('ac_handling', DEFAULTS_MAIN['ac_handling'])
    ac_names = {0: 'None', 1: 'DiscardAll', 2: 'KeepUnits', 3: 'KeepOrientable'}
    if ac != DEFAULTS_MAIN['ac_handling']:
        emit(f"--ac-handling={ac_names.get(ac, str(ac))}")

    if not main.get('ac_res_aggressive', True):
        emit('--ac-non-aggressive')

    # ── Simplification ────────────────────────────────────────────────

    if main.get('forward_context_sr_aggressive', False):
        emit('--forward-context-sr-aggressive')  # implies --forward-context-sr
    elif main.get('forward_context_sr', False):
        emit('--forward-context-sr')

    if main.get('backward_context_sr', False):
        emit('--backward-context-sr')

    if main.get('forward_subsumption_aggressive', False):
        emit('--fw-subsumption-aggressive')

    fd = main.get('forward_demod', DEFAULTS_MAIN['forward_demod'])
    opt('forward-demod-level', fd, DEFAULTS_MAIN['forward_demod'])

    if main.get('prefer_general', False):
        emit('--prefer-general-demodulators')

    ca = main.get('condensing_aggressive', False)
    c  = main.get('condensing', False)
    if ca:
        emit('--condense-aggressive')  # implies --condense
    elif c:
        emit('--condense')

    # ── Destructive ER ────────────────────────────────────────────────

    # --destructive-er-aggressive implies er_varlit_destructive but NOT er_strong_destructive
    if main.get('er_aggressive', False):
        emit('--destructive-er-aggressive')  # implies --destructive-er
        if main.get('er_strong_destructive', False):
            emit('--strong-destructive-er')
    elif main.get('er_strong_destructive', False):
        emit('--strong-destructive-er')
    elif main.get('er_varlit_destructive', False):
        emit('--destructive-er')

    # ── Splitting ─────────────────────────────────────────────────────

    sc = main.get('split_clauses', 0)
    opt('split-clauses', sc, 0)
    if sc:
        opt('split-method', main.get('split_method', 0), 0)
        if main.get('split_aggressive', False):
            emit('--split-aggressive')
        if not main.get('split_fresh_defs', True):
            emit('--split-reuse-defs')

    # ── Disequality decomposition ─────────────────────────────────────

    dd = main.get('diseq_decomposition', 0)
    opt('disequality-decomposition', dd, 0)
    if dd:
        da = main.get('diseq_decomp_maxarity', LLONG_MAX)
        if da != LLONG_MAX:
            emit(f'--disequality-decomp-maxarity={da}')

    # ── Indexing ──────────────────────────────────────────────────────

    opt('rw-bw-index',    main.get('rw_bw_index_type',  'FP7'), 'FP7')
    opt('pm-from-index',  main.get('pm_from_index_type', 'FP7'), 'FP7')
    opt('pm-into-index',  main.get('pm_into_index_type', 'FP7'), 'FP7')

    # ── SAT checking ──────────────────────────────────────────────────

    step  = main.get('sat_check_step_limit',     LLONG_MAX)
    size  = main.get('sat_check_size_limit',     LLONG_MAX)
    ttins = main.get('sat_check_ttinsert_limit', LLONG_MAX)
    gnd   = main.get('sat_check_grounding',      DEFAULTS_MAIN['sat_check_grounding'])

    if step != LLONG_MAX:
        emit(f'--satcheck-proc-interval={step}')
    if size != LLONG_MAX:
        emit(f'--satcheck-gen-interval={size}')
    if ttins != LLONG_MAX:
        emit(f'--satcheck-ttinsert-interval={ttins}')
    if gnd != DEFAULTS_MAIN['sat_check_grounding']:
        emit(f'--satcheck={gnd}')

    if main.get('sat_check_normconst', False):
        emit('--satcheck-normalize-const')
    if main.get('sat_check_normalize', False):
        emit('--satcheck-normalize-unproc')

    sdl = main.get('sat_check_decision_limit', DEFAULTS_MAIN['sat_check_decision_limit'])
    opt('satcheck-decision-limit', sdl, DEFAULTS_MAIN['sat_check_decision_limit'])

    # ── Limits ────────────────────────────────────────────────────────

    fol = main.get('filter_orphans_limit', LLONG_MAX)
    if fol != LLONG_MAX:
        emit(f'--filter-orphans-limit={fol}')

    fcl = main.get('forward_contract_limit', LLONG_MAX)
    if fcl != LLONG_MAX:
        emit(f'--forward-contract-limit={fcl}')

    dbl = main.get('delete_bad_limit', LLONG_MAX)
    if dbl != LLONG_MAX:
        emit(f'--delete-bad-limit={dbl}')

    meml = main.get('mem_limit', 0)
    if meml:
        emit(f'--memory-limit={meml // (1024*1024)}')

    # ── Watchlist / SOS ───────────────────────────────────────────────

    if not main.get('watchlist_simplify', True):
        emit('--no-watchlist-simplification')

    if main.get('use_tptp_sos', False):
        emit('--sos-uses-input-types')

    # ── Misc ──────────────────────────────────────────────────────────

    if not main.get('watchlist_is_static', False) and \
       main.get('watchlist_is_static') is not None:
        pass  # False is default; True would need a file argument, skip

    if main.get('detsort_bw_rw', False):
        emit('--detsort-rw')
    if main.get('detsort_tmpset', False):
        emit('--detsort-new')

    # ── HO extensions ─────────────────────────────────────────────────

    ac_val = main.get('arg_cong', DEFAULTS_MAIN['arg_cong'])
    opt('arg-cong', ac_val, DEFAULTS_MAIN['arg_cong'])

    ne_val = main.get('neg_ext', DEFAULTS_MAIN['neg_ext'])
    opt('neg-ext', ne_val, DEFAULTS_MAIN['neg_ext'])

    pe_val = main.get('pos_ext', DEFAULTS_MAIN['pos_ext'])
    opt('pos-ext', pe_val, DEFAULTS_MAIN['pos_ext'])

    esd = main.get('ext_rules_max_depth', -1)
    opt('ext-sup-max-depth', esd, -1)

    if main.get('inverse_recognition', False):
        emit('--inverse-recognition')
    if main.get('replace_inj_defs', False):
        emit('--replace-inj-defs')

    opt('lift-lambdas',        main.get('lift_lambdas',        True),  True)
    opt('cnf-lambda-to-forall',main.get('lambda_to_forall',    True),  True)
    opt('unroll-formulas-only',main.get('unroll_only_formulas', True),  True)

    elmd = main.get('elim_leibniz_max_depth', -1)
    opt('eliminate-leibniz-eq', elmd, -1)

    pem = main.get('prim_enum_mode', DEFAULTS_MAIN['prim_enum_mode'])
    opt('prim-enum-mode', pem, DEFAULTS_MAIN['prim_enum_mode'])

    pemd = main.get('prim_enum_max_depth', -1)
    opt('prim-enum-max-depth', pemd, -1)

    icd = main.get('inst_choice_max_depth', -1)
    opt('inst-choice-max-depth', icd, -1)

    opt('local-rw',   main.get('local_rw',  False), False)
    opt('prune-args', main.get('prune_args', False), False)

    if main.get('preinstantiate_induction', False):
        emit('--preinstantiate-induction=true')

    opt('fool-unroll', main.get('fool_unroll', True), True)

    opt('func-proj-limit', main.get('func_proj_limit', 0), 0)
    opt('imit-limit',      main.get('imit_limit',      0), 0)
    opt('ident-limit',     main.get('ident_limit',     0), 0)
    opt('elim-limit',      main.get('elim_limit',      0), 0)

    opt('unif-mode',       main.get('unif_mode',       'single'), 'single')
    opt('pattern-oracle',  main.get('pattern_oracle',  True),     True)
    opt('fixpoint-oracle', main.get('fixpoint_oracle', True),     True)
    opt('max-unifiers',    main.get('max_unifiers',    4),        4)
    opt('max-unif-steps',  main.get('max_unif_steps',  256),      256)

    return args + heuristic_arg, warnings


def main():
    import os, subprocess, argparse

    parser = argparse.ArgumentParser(
        prog='strategy2args.py',
        description='Convert eprover --print-strategy output to CLI arguments.',
        epilog=(
            'Examples:\n'
            '  strategy2args.py new_bool_5\n'
            '  eprover-ho --print-strategy=new_bool_5 | strategy2args.py -\n'
            '  eprover-ho --print-strategy=new_bool_5 > strat.txt && strategy2args.py strat.txt'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('input', help='strategy name, file path, or - for stdin')
    parser.add_argument('-1', '--one-line', action='store_true',
                        help='print all arguments on one line')
    parser.add_argument('-s', '--no-sine', action='store_true',
                        help='omit --sine argument')
    opts = parser.parse_args()

    arg = opts.input
    if arg == '-':
        text = sys.stdin.read()
    elif os.path.exists(arg):
        with open(arg) as f:
            text = f.read()
    else:
        # Treat as a strategy name — ask eprover-ho
        result = subprocess.run(
            ['eprover-ho', f'--print-strategy={arg}'],
            capture_output=True, text=True, stdin=subprocess.DEVNULL
        )
        if result.returncode != 0:
            print(result.stderr, end='', file=sys.stderr)
            sys.exit(result.returncode)
        text = result.stdout

    args, warnings = strategy_to_args(text, no_sine=opts.no_sine)

    for w in warnings:
        print(w, file=sys.stderr)

    if opts.one_line:
        print(' '.join(args))
    else:
        print(' \\\n  '.join(args))


if __name__ == '__main__':
    main()
