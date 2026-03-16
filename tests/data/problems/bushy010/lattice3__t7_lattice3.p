%------------------------------------------------------------------------------
% File     : lattice3__t7_lattice3

% Syntax   : Number of formulae    :  133 (  28 unit)
%            Number of atoms       :  603 (  33 equality)
%            Maximal formula depth :   17 (   6 average)
%            Number of connectives :  570 ( 100 ~  ;   1  |; 361  &)
%                                         (   4 <=>; 104 =>;   0 <=)
%                                         (   0 <~>;   0 ~|;   0 ~&)
%            Number of predicates  :   54 (   1 propositional; 0-3 arity)
%            Number of functors    :   24 (   1 constant; 0-4 arity)
%            Number of variables   :  211 (   1 singleton; 175 !;  36 ?)
%            Maximal term depth    :    3 (   1 average)
%------------------------------------------------------------------------------
fof(abstractness_v1_lattices,axiom,(
    ! [A] : 
      ( meet_semilatt_str(A)
     => ( strict_meet_semilatt_str(A)
       => A = meet_semilatt_str_of(the_carrier(A),the_L_meet(A)) ) ) )).

fof(abstractness_v1_orders_2,axiom,(
    ! [A] : 
      ( rel_str(A)
     => ( strict_rel_str(A)
       => A = rel_str_of(the_carrier(A),the_InternalRel(A)) ) ) )).

fof(abstractness_v1_struct_0,axiom,(
    ! [A] : 
      ( one_sorted_str(A)
     => ( strict_one_sorted(A)
       => A = one_sorted_str_of(the_carrier(A)) ) ) )).

fof(abstractness_v2_lattices,axiom,(
    ! [A] : 
      ( join_semilatt_str(A)
     => ( strict_join_semilatt_str(A)
       => A = join_semilatt_str_of(the_carrier(A),the_L_join(A)) ) ) )).

fof(abstractness_v2_struct_0,axiom,(
    ! [A] : 
      ( zero_str(A)
     => ( strict_zero_str(A)
       => A = zero_str_of(the_carrier(A),the_zero(A)) ) ) )).

fof(abstractness_v3_lattices,axiom,(
    ! [A] : 
      ( latt_str(A)
     => ( strict_latt_str(A)
       => A = latt_str_of(the_carrier(A),the_L_join(A),the_L_meet(A)) ) ) )).

fof(antisymmetry_r2_hidden,axiom,(
    ! [A,B] : 
      ( in(A,B)
     => ~ in(B,A) ) )).

fof(cc1_lattice2,axiom,(
    ! [A] : 
      ( latt_str(A)
     => ( ( ~ empty_carrier(A)
          & lattice(A)
          & v1_lattice2(A) )
       => ( ~ empty_carrier(A)
          & join_commutative(A)
          & join_associative(A)
          & meet_commutative(A)
          & meet_associative(A)
          & meet_absorbing(A)
          & join_absorbing(A)
          & lattice(A)
          & lower_bounded_semilattstr(A)
          & v3_filter_0(A) ) ) ) )).

fof(cc1_lattices,axiom,(
    ! [A] : 
      ( latt_str(A)
     => ( ( ~ empty_carrier(A)
          & lattice(A) )
       => ( ~ empty_carrier(A)
          & join_commutative(A)
          & join_associative(A)
          & meet_commutative(A)
          & meet_associative(A)
          & meet_absorbing(A)
          & join_absorbing(A) ) ) ) )).

fof(cc1_relset_1,axiom,(
    ! [A,B,C] : 
      ( element(C,powerset(cartesian_product2(A,B)))
     => relation(C) ) )).

fof(cc2_lattice2,axiom,(
    ! [A] : 
      ( latt_str(A)
     => ( ( ~ empty_carrier(A)
          & lattice(A)
          & lower_bounded_semilattstr(A)
          & v3_filter_0(A) )
       => ( ~ empty_carrier(A)
          & join_commutative(A)
          & join_associative(A)
          & meet_commutative(A)
          & meet_associative(A)
          & meet_absorbing(A)
          & join_absorbing(A)
          & lattice(A)
          & v1_lattice2(A) ) ) ) )).

fof(cc2_lattices,axiom,(
    ! [A] : 
      ( latt_str(A)
     => ( ( ~ empty_carrier(A)
          & join_commutative(A)
          & join_associative(A)
          & meet_commutative(A)
          & meet_associative(A)
          & meet_absorbing(A)
          & join_absorbing(A) )
       => ( ~ empty_carrier(A)
          & lattice(A) ) ) ) )).

fof(cc3_lattices,axiom,(
    ! [A] : 
      ( latt_str(A)
     => ( ( ~ empty_carrier(A)
          & lower_bounded_semilattstr(A)
          & upper_bounded_semilattstr(A) )
       => ( ~ empty_carrier(A)
          & bounded_lattstr(A) ) ) ) )).

fof(cc4_lattices,axiom,(
    ! [A] : 
      ( latt_str(A)
     => ( ( ~ empty_carrier(A)
          & bounded_lattstr(A) )
       => ( ~ empty_carrier(A)
          & lower_bounded_semilattstr(A)
          & upper_bounded_semilattstr(A) ) ) ) )).

fof(cc5_lattices,axiom,(
    ! [A] : 
      ( latt_str(A)
     => ( ( ~ empty_carrier(A)
          & boolean_lattstr(A) )
       => ( ~ empty_carrier(A)
          & distributive_lattstr(A)
          & lower_bounded_semilattstr(A)
          & upper_bounded_semilattstr(A)
          & bounded_lattstr(A)
          & complemented_lattstr(A) ) ) ) )).

fof(cc6_lattices,axiom,(
    ! [A] : 
      ( latt_str(A)
     => ( ( ~ empty_carrier(A)
          & distributive_lattstr(A)
          & bounded_lattstr(A)
          & complemented_lattstr(A) )
       => ( ~ empty_carrier(A)
          & boolean_lattstr(A) ) ) ) )).

fof(cc7_lattices,axiom,(
    ! [A] : 
      ( latt_str(A)
     => ( ( ~ empty_carrier(A)
          & lattice(A)
          & distributive_lattstr(A) )
       => ( ~ empty_carrier(A)
          & join_commutative(A)
          & join_associative(A)
          & meet_commutative(A)
          & meet_associative(A)
          & meet_absorbing(A)
          & join_absorbing(A)
          & lattice(A)
          & modular_lattstr(A) ) ) ) )).

fof(commutativity_k2_tarski,axiom,(
    ! [A,B] : unordered_pair(A,B) = unordered_pair(B,A) )).

fof(d2_lattice3,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & lattice(A)
        & latt_str(A) )
     => poset_of_lattice(A) = rel_str_of(the_carrier(A),k2_lattice3(A)) ) )).

fof(d3_lattice3,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & lattice(A)
        & latt_str(A) )
     => ! [B] : 
          ( element(B,the_carrier(A))
         => cast_to_el_of_LattPOSet(A,B) = B ) ) )).

fof(d5_tarski,axiom,(
    ! [A,B] : ordered_pair(A,B) = unordered_pair(unordered_pair(A,B),singleton(A)) )).

fof(d9_orders_2,axiom,(
    ! [A] : 
      ( rel_str(A)
     => ! [B] : 
          ( element(B,the_carrier(A))
         => ! [C] : 
              ( element(C,the_carrier(A))
             => ( ~ ( related(A,B,C)
                    & ~ in(ordered_pair(B,C),the_InternalRel(A)) )
                & ~ ( in(ordered_pair(B,C),the_InternalRel(A))
                    & ~ related(A,B,C) ) ) ) ) ) )).

fof(dt_g1_lattices,axiom,(
    ! [A,B] : 
      ( ( function(B)
        & quasi_total(B,cartesian_product2(A,A),A)
        & relation_of2(B,cartesian_product2(A,A),A) )
     => ( strict_meet_semilatt_str(meet_semilatt_str_of(A,B))
        & meet_semilatt_str(meet_semilatt_str_of(A,B)) ) ) )).

fof(dt_g1_orders_2,axiom,(
    ! [A,B] : 
      ( relation_of2(B,A,A)
     => ( strict_rel_str(rel_str_of(A,B))
        & rel_str(rel_str_of(A,B)) ) ) )).

fof(dt_g1_struct_0,axiom,(
    ! [A] : 
      ( strict_one_sorted(one_sorted_str_of(A))
      & one_sorted_str(one_sorted_str_of(A)) ) )).

fof(dt_g2_lattices,axiom,(
    ! [A,B] : 
      ( ( function(B)
        & quasi_total(B,cartesian_product2(A,A),A)
        & relation_of2(B,cartesian_product2(A,A),A) )
     => ( strict_join_semilatt_str(join_semilatt_str_of(A,B))
        & join_semilatt_str(join_semilatt_str_of(A,B)) ) ) )).

fof(dt_g2_struct_0,axiom,(
    ! [A,B] : 
      ( element(B,A)
     => ( strict_zero_str(zero_str_of(A,B))
        & zero_str(zero_str_of(A,B)) ) ) )).

fof(dt_g3_lattices,axiom,(
    ! [A,B,C] : 
      ( ( function(B)
        & quasi_total(B,cartesian_product2(A,A),A)
        & relation_of2(B,cartesian_product2(A,A),A)
        & function(C)
        & quasi_total(C,cartesian_product2(A,A),A)
        & relation_of2(C,cartesian_product2(A,A),A) )
     => ( strict_latt_str(latt_str_of(A,B,C))
        & latt_str(latt_str_of(A,B,C)) ) ) )).

fof(dt_k10_filter_1,axiom,(
    ! [A,B,C,D] : 
      ( ( ~ empty_carrier(A)
        & lattice(A)
        & latt_str(A)
        & ~ empty_carrier(B)
        & lattice(B)
        & latt_str(B)
        & element(C,the_carrier(A))
        & element(D,the_carrier(B)) )
     => element(k10_filter_1(A,B,C,D),the_carrier(k8_filter_1(A,B))) ) )).

fof(dt_k1_domain_1,axiom,(
    ! [A,B,C,D] : 
      ( ( ~ empty(A)
        & ~ empty(B)
        & element(C,A)
        & element(D,B) )
     => element(ordered_pair_as_product_element(A,B,C,D),cartesian_product2(A,B)) ) )).

fof(dt_k1_tarski,axiom,(
    $true )).

fof(dt_k1_xboole_0,axiom,(
    $true )).

fof(dt_k1_zfmisc_1,axiom,(
    $true )).

fof(dt_k2_lattice3,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & lattice(A)
        & latt_str(A) )
     => ( reflexive(k2_lattice3(A))
        & antisymmetric(k2_lattice3(A))
        & transitive(k2_lattice3(A))
        & v1_partfun1(k2_lattice3(A),the_carrier(A),the_carrier(A))
        & relation_of2_as_subset(k2_lattice3(A),the_carrier(A),the_carrier(A)) ) ) )).

fof(dt_k2_tarski,axiom,(
    $true )).

fof(dt_k2_zfmisc_1,axiom,(
    $true )).

fof(dt_k3_lattice3,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & lattice(A)
        & latt_str(A) )
     => ( strict_rel_str(poset_of_lattice(A))
        & reflexive_relstr(poset_of_lattice(A))
        & transitive_relstr(poset_of_lattice(A))
        & antisymmetric_relstr(poset_of_lattice(A))
        & rel_str(poset_of_lattice(A)) ) ) )).

fof(dt_k4_lattice3,axiom,(
    ! [A,B] : 
      ( ( ~ empty_carrier(A)
        & lattice(A)
        & latt_str(A)
        & element(B,the_carrier(A)) )
     => element(cast_to_el_of_LattPOSet(A,B),the_carrier(poset_of_lattice(A))) ) )).

fof(dt_k4_tarski,axiom,(
    $true )).

fof(dt_k8_filter_1,axiom,(
    ! [A,B] : 
      ( ( ~ empty_carrier(A)
        & latt_str(A)
        & ~ empty_carrier(B)
        & latt_str(B) )
     => ( strict_latt_str(k8_filter_1(A,B))
        & latt_str(k8_filter_1(A,B)) ) ) )).

fof(dt_k9_filter_1,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & lattice(A)
        & latt_str(A) )
     => relation(relation_of_lattice(A)) ) )).

fof(dt_l1_lattices,axiom,(
    ! [A] : 
      ( meet_semilatt_str(A)
     => one_sorted_str(A) ) )).

fof(dt_l1_orders_2,axiom,(
    ! [A] : 
      ( rel_str(A)
     => one_sorted_str(A) ) )).

fof(dt_l1_struct_0,axiom,(
    $true )).

fof(dt_l2_lattices,axiom,(
    ! [A] : 
      ( join_semilatt_str(A)
     => one_sorted_str(A) ) )).

fof(dt_l2_struct_0,axiom,(
    ! [A] : 
      ( zero_str(A)
     => one_sorted_str(A) ) )).

fof(dt_l3_lattices,axiom,(
    ! [A] : 
      ( latt_str(A)
     => ( meet_semilatt_str(A)
        & join_semilatt_str(A) ) ) )).

fof(dt_m1_relset_1,axiom,(
    $true )).

fof(dt_m1_subset_1,axiom,(
    $true )).

fof(dt_m2_relset_1,axiom,(
    ! [A,B,C] : 
      ( relation_of2_as_subset(C,A,B)
     => element(C,powerset(cartesian_product2(A,B))) ) )).

fof(dt_u1_lattices,axiom,(
    ! [A] : 
      ( meet_semilatt_str(A)
     => ( function(the_L_meet(A))
        & quasi_total(the_L_meet(A),cartesian_product2(the_carrier(A),the_carrier(A)),the_carrier(A))
        & relation_of2_as_subset(the_L_meet(A),cartesian_product2(the_carrier(A),the_carrier(A)),the_carrier(A)) ) ) )).

fof(dt_u1_orders_2,axiom,(
    ! [A] : 
      ( rel_str(A)
     => relation_of2_as_subset(the_InternalRel(A),the_carrier(A),the_carrier(A)) ) )).

fof(dt_u1_struct_0,axiom,(
    $true )).

fof(dt_u2_lattices,axiom,(
    ! [A] : 
      ( join_semilatt_str(A)
     => ( function(the_L_join(A))
        & quasi_total(the_L_join(A),cartesian_product2(the_carrier(A),the_carrier(A)),the_carrier(A))
        & relation_of2_as_subset(the_L_join(A),cartesian_product2(the_carrier(A),the_carrier(A)),the_carrier(A)) ) ) )).

fof(dt_u2_struct_0,axiom,(
    ! [A] : 
      ( zero_str(A)
     => element(the_zero(A),the_carrier(A)) ) )).

fof(existence_l1_lattices,axiom,(
    ? [A] : meet_semilatt_str(A) )).

fof(existence_l1_orders_2,axiom,(
    ? [A] : rel_str(A) )).

fof(existence_l1_struct_0,axiom,(
    ? [A] : one_sorted_str(A) )).

fof(existence_l2_lattices,axiom,(
    ? [A] : join_semilatt_str(A) )).

fof(existence_l2_struct_0,axiom,(
    ? [A] : zero_str(A) )).

fof(existence_l3_lattices,axiom,(
    ? [A] : latt_str(A) )).

fof(existence_m1_relset_1,axiom,(
    ! [A,B] : 
    ? [C] : relation_of2(C,A,B) )).

fof(existence_m1_subset_1,axiom,(
    ! [A] : 
    ? [B] : element(B,A) )).

fof(existence_m2_relset_1,axiom,(
    ! [A,B] : 
    ? [C] : relation_of2_as_subset(C,A,B) )).

fof(fc1_lattices,axiom,(
    ! [A,B] : 
      ( ( ~ empty(A)
        & function(B)
        & quasi_total(B,cartesian_product2(A,A),A)
        & relation_of2(B,cartesian_product2(A,A),A) )
     => ( ~ empty_carrier(join_semilatt_str_of(A,B))
        & strict_join_semilatt_str(join_semilatt_str_of(A,B)) ) ) )).

fof(fc1_orders_2,axiom,(
    ! [A,B] : 
      ( ( ~ empty(A)
        & relation_of2(B,A,A) )
     => ( ~ empty_carrier(rel_str_of(A,B))
        & strict_rel_str(rel_str_of(A,B)) ) ) )).

fof(fc1_struct_0,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & one_sorted_str(A) )
     => ~ empty(the_carrier(A)) ) )).

fof(fc1_subset_1,axiom,(
    ! [A] : ~ empty(powerset(A)) )).

fof(fc1_xboole_0,axiom,(
    empty(empty_set) )).

fof(fc2_lattice2,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & join_commutative(A)
        & join_semilatt_str(A) )
     => ( relation(the_L_join(A))
        & function(the_L_join(A))
        & quasi_total(the_L_join(A),cartesian_product2(the_carrier(A),the_carrier(A)),the_carrier(A))
        & v1_binop_1(the_L_join(A),the_carrier(A))
        & v1_partfun1(the_L_join(A),cartesian_product2(the_carrier(A),the_carrier(A)),the_carrier(A)) ) ) )).

fof(fc2_lattices,axiom,(
    ! [A,B] : 
      ( ( ~ empty(A)
        & function(B)
        & quasi_total(B,cartesian_product2(A,A),A)
        & relation_of2(B,cartesian_product2(A,A),A) )
     => ( ~ empty_carrier(meet_semilatt_str_of(A,B))
        & strict_meet_semilatt_str(meet_semilatt_str_of(A,B)) ) ) )).

fof(fc2_orders_2,axiom,(
    ! [A] : 
      ( ( reflexive_relstr(A)
        & transitive_relstr(A)
        & antisymmetric_relstr(A)
        & rel_str(A) )
     => ( relation(the_InternalRel(A))
        & reflexive(the_InternalRel(A))
        & antisymmetric(the_InternalRel(A))
        & transitive(the_InternalRel(A))
        & v1_partfun1(the_InternalRel(A),the_carrier(A),the_carrier(A)) ) ) )).

fof(fc2_subset_1,axiom,(
    ! [A] : ~ empty(singleton(A)) )).

fof(fc3_lattice2,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & join_associative(A)
        & join_semilatt_str(A) )
     => ( relation(the_L_join(A))
        & function(the_L_join(A))
        & quasi_total(the_L_join(A),cartesian_product2(the_carrier(A),the_carrier(A)),the_carrier(A))
        & v2_binop_1(the_L_join(A),the_carrier(A))
        & v1_partfun1(the_L_join(A),cartesian_product2(the_carrier(A),the_carrier(A)),the_carrier(A)) ) ) )).

fof(fc3_lattices,axiom,(
    ! [A,B,C] : 
      ( ( ~ empty(A)
        & function(B)
        & quasi_total(B,cartesian_product2(A,A),A)
        & relation_of2(B,cartesian_product2(A,A),A)
        & function(C)
        & quasi_total(C,cartesian_product2(A,A),A)
        & relation_of2(C,cartesian_product2(A,A),A) )
     => ( ~ empty_carrier(latt_str_of(A,B,C))
        & strict_latt_str(latt_str_of(A,B,C)) ) ) )).

fof(fc3_orders_2,axiom,(
    ! [A,B] : 
      ( ( reflexive(B)
        & antisymmetric(B)
        & transitive(B)
        & v1_partfun1(B,A,A)
        & relation_of2(B,A,A) )
     => ( strict_rel_str(rel_str_of(A,B))
        & reflexive_relstr(rel_str_of(A,B))
        & transitive_relstr(rel_str_of(A,B))
        & antisymmetric_relstr(rel_str_of(A,B)) ) ) )).

fof(fc3_subset_1,axiom,(
    ! [A,B] : ~ empty(unordered_pair(A,B)) )).

fof(fc4_lattice2,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & meet_commutative(A)
        & meet_semilatt_str(A) )
     => ( relation(the_L_meet(A))
        & function(the_L_meet(A))
        & quasi_total(the_L_meet(A),cartesian_product2(the_carrier(A),the_carrier(A)),the_carrier(A))
        & v1_binop_1(the_L_meet(A),the_carrier(A))
        & v1_partfun1(the_L_meet(A),cartesian_product2(the_carrier(A),the_carrier(A)),the_carrier(A)) ) ) )).

fof(fc4_lattice3,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & lattice(A)
        & latt_str(A) )
     => ( ~ empty_carrier(poset_of_lattice(A))
        & strict_rel_str(poset_of_lattice(A))
        & reflexive_relstr(poset_of_lattice(A))
        & transitive_relstr(poset_of_lattice(A))
        & antisymmetric_relstr(poset_of_lattice(A)) ) ) )).

fof(fc4_subset_1,axiom,(
    ! [A,B] : 
      ( ( ~ empty(A)
        & ~ empty(B) )
     => ~ empty(cartesian_product2(A,B)) ) )).

fof(fc5_lattice2,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & meet_associative(A)
        & meet_semilatt_str(A) )
     => ( relation(the_L_meet(A))
        & function(the_L_meet(A))
        & quasi_total(the_L_meet(A),cartesian_product2(the_carrier(A),the_carrier(A)),the_carrier(A))
        & v2_binop_1(the_L_meet(A),the_carrier(A))
        & v1_partfun1(the_L_meet(A),cartesian_product2(the_carrier(A),the_carrier(A)),the_carrier(A)) ) ) )).

fof(free_g1_lattices,axiom,(
    ! [A,B] : 
      ( ( function(B)
        & quasi_total(B,cartesian_product2(A,A),A)
        & relation_of2(B,cartesian_product2(A,A),A) )
     => ! [C,D] : 
          ( meet_semilatt_str_of(A,B) = meet_semilatt_str_of(C,D)
         => ( A = C
            & B = D ) ) ) )).

fof(free_g1_orders_2,axiom,(
    ! [A,B] : 
      ( relation_of2(B,A,A)
     => ! [C,D] : 
          ( rel_str_of(A,B) = rel_str_of(C,D)
         => ( A = C
            & B = D ) ) ) )).

fof(free_g1_struct_0,axiom,(
    ! [A,B] : 
      ( one_sorted_str_of(A) = one_sorted_str_of(B)
     => A = B ) )).

fof(free_g2_lattices,axiom,(
    ! [A,B] : 
      ( ( function(B)
        & quasi_total(B,cartesian_product2(A,A),A)
        & relation_of2(B,cartesian_product2(A,A),A) )
     => ! [C,D] : 
          ( join_semilatt_str_of(A,B) = join_semilatt_str_of(C,D)
         => ( A = C
            & B = D ) ) ) )).

fof(free_g2_struct_0,axiom,(
    ! [A,B] : 
      ( element(B,A)
     => ! [C,D] : 
          ( zero_str_of(A,B) = zero_str_of(C,D)
         => ( A = C
            & B = D ) ) ) )).

fof(free_g3_lattices,axiom,(
    ! [A,B,C] : 
      ( ( function(B)
        & quasi_total(B,cartesian_product2(A,A),A)
        & relation_of2(B,cartesian_product2(A,A),A)
        & function(C)
        & quasi_total(C,cartesian_product2(A,A),A)
        & relation_of2(C,cartesian_product2(A,A),A) )
     => ! [D,E,F] : 
          ( latt_str_of(A,B,C) = latt_str_of(D,E,F)
         => ( A = D
            & B = E
            & C = F ) ) ) )).

fof(rc10_lattices,axiom,(
    ? [A] : 
      ( latt_str(A)
      & ~ empty_carrier(A)
      & strict_latt_str(A)
      & join_commutative(A)
      & join_associative(A)
      & meet_commutative(A)
      & meet_associative(A)
      & meet_absorbing(A)
      & join_absorbing(A)
      & lattice(A)
      & distributive_lattstr(A)
      & modular_lattstr(A)
      & lower_bounded_semilattstr(A)
      & upper_bounded_semilattstr(A) ) )).

fof(rc11_lattices,axiom,(
    ? [A] : 
      ( latt_str(A)
      & ~ empty_carrier(A)
      & strict_latt_str(A)
      & join_commutative(A)
      & join_associative(A)
      & meet_commutative(A)
      & meet_associative(A)
      & meet_absorbing(A)
      & join_absorbing(A)
      & lattice(A)
      & lower_bounded_semilattstr(A)
      & upper_bounded_semilattstr(A)
      & bounded_lattstr(A) ) )).

fof(rc12_lattices,axiom,(
    ? [A] : 
      ( latt_str(A)
      & ~ empty_carrier(A)
      & strict_latt_str(A)
      & join_commutative(A)
      & join_associative(A)
      & meet_commutative(A)
      & meet_associative(A)
      & meet_absorbing(A)
      & join_absorbing(A)
      & lattice(A)
      & lower_bounded_semilattstr(A)
      & upper_bounded_semilattstr(A)
      & bounded_lattstr(A)
      & complemented_lattstr(A) ) )).

fof(rc13_lattices,axiom,(
    ? [A] : 
      ( latt_str(A)
      & ~ empty_carrier(A)
      & strict_latt_str(A)
      & join_commutative(A)
      & join_associative(A)
      & meet_commutative(A)
      & meet_associative(A)
      & meet_absorbing(A)
      & join_absorbing(A)
      & lattice(A)
      & distributive_lattstr(A)
      & lower_bounded_semilattstr(A)
      & upper_bounded_semilattstr(A)
      & bounded_lattstr(A)
      & complemented_lattstr(A)
      & boolean_lattstr(A) ) )).

fof(rc1_lattice2,axiom,(
    ? [A] : 
      ( latt_str(A)
      & ~ empty_carrier(A)
      & join_commutative(A)
      & join_associative(A)
      & meet_commutative(A)
      & meet_associative(A)
      & meet_absorbing(A)
      & join_absorbing(A)
      & lattice(A)
      & v1_lattice2(A) ) )).

fof(rc1_lattices,axiom,(
    ? [A] : 
      ( meet_semilatt_str(A)
      & strict_meet_semilatt_str(A) ) )).

fof(rc1_orders_2,axiom,(
    ? [A] : 
      ( rel_str(A)
      & strict_rel_str(A) ) )).

fof(rc1_struct_0,axiom,(
    ? [A] : 
      ( one_sorted_str(A)
      & strict_one_sorted(A) ) )).

fof(rc1_subset_1,axiom,(
    ! [A] : 
      ( ~ empty(A)
     => ? [B] : 
          ( element(B,powerset(A))
          & ~ empty(B) ) ) )).

fof(rc1_xboole_0,axiom,(
    ? [A] : empty(A) )).

fof(rc2_lattice2,axiom,(
    ? [A] : 
      ( latt_str(A)
      & ~ empty_carrier(A)
      & strict_latt_str(A)
      & join_commutative(A)
      & join_associative(A)
      & meet_commutative(A)
      & meet_associative(A)
      & meet_absorbing(A)
      & join_absorbing(A)
      & lattice(A)
      & lower_bounded_semilattstr(A)
      & v3_filter_0(A)
      & v1_lattice2(A) ) )).

fof(rc2_lattices,axiom,(
    ? [A] : 
      ( join_semilatt_str(A)
      & strict_join_semilatt_str(A) ) )).

fof(rc2_orders_2,axiom,(
    ? [A] : 
      ( rel_str(A)
      & ~ empty_carrier(A)
      & strict_rel_str(A)
      & reflexive_relstr(A)
      & transitive_relstr(A)
      & antisymmetric_relstr(A) ) )).

fof(rc2_struct_0,axiom,(
    ? [A] : 
      ( zero_str(A)
      & strict_zero_str(A) ) )).

fof(rc2_subset_1,axiom,(
    ! [A] : 
    ? [B] : 
      ( element(B,powerset(A))
      & empty(B) ) )).

fof(rc2_xboole_0,axiom,(
    ? [A] : ~ empty(A) )).

fof(rc3_lattices,axiom,(
    ? [A] : 
      ( latt_str(A)
      & strict_latt_str(A) ) )).

fof(rc3_orders_2,axiom,(
    ! [A] : 
      ( rel_str(A)
     => ? [B] : 
          ( element(B,powerset(the_carrier(A)))
          & strongly_connected_rel_subset(B,A) ) ) )).

fof(rc3_struct_0,axiom,(
    ? [A] : 
      ( one_sorted_str(A)
      & ~ empty_carrier(A) ) )).

fof(rc4_lattices,axiom,(
    ? [A] : 
      ( join_semilatt_str(A)
      & ~ empty_carrier(A)
      & strict_join_semilatt_str(A) ) )).

fof(rc4_struct_0,axiom,(
    ? [A] : 
      ( zero_str(A)
      & ~ empty_carrier(A) ) )).

fof(rc5_lattices,axiom,(
    ? [A] : 
      ( meet_semilatt_str(A)
      & ~ empty_carrier(A)
      & strict_meet_semilatt_str(A) ) )).

fof(rc5_struct_0,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & one_sorted_str(A) )
     => ? [B] : 
          ( element(B,powerset(the_carrier(A)))
          & ~ empty(B) ) ) )).

fof(rc6_lattices,axiom,(
    ? [A] : 
      ( latt_str(A)
      & ~ empty_carrier(A)
      & strict_latt_str(A) ) )).

fof(rc7_lattices,axiom,(
    ? [A] : 
      ( join_semilatt_str(A)
      & ~ empty_carrier(A)
      & strict_join_semilatt_str(A)
      & join_commutative(A)
      & join_associative(A) ) )).

fof(rc8_lattices,axiom,(
    ? [A] : 
      ( meet_semilatt_str(A)
      & ~ empty_carrier(A)
      & strict_meet_semilatt_str(A)
      & meet_commutative(A)
      & meet_associative(A) ) )).

fof(rc9_lattices,axiom,(
    ? [A] : 
      ( latt_str(A)
      & ~ empty_carrier(A)
      & strict_latt_str(A)
      & join_commutative(A)
      & join_associative(A)
      & meet_commutative(A)
      & meet_associative(A)
      & meet_absorbing(A)
      & join_absorbing(A)
      & lattice(A) ) )).

fof(redefinition_k10_filter_1,axiom,(
    ! [A,B,C,D] : 
      ( ( ~ empty_carrier(A)
        & lattice(A)
        & latt_str(A)
        & ~ empty_carrier(B)
        & lattice(B)
        & latt_str(B)
        & element(C,the_carrier(A))
        & element(D,the_carrier(B)) )
     => k10_filter_1(A,B,C,D) = ordered_pair(C,D) ) )).

fof(redefinition_k1_domain_1,axiom,(
    ! [A,B,C,D] : 
      ( ( ~ empty(A)
        & ~ empty(B)
        & element(C,A)
        & element(D,B) )
     => ordered_pair_as_product_element(A,B,C,D) = ordered_pair(C,D) ) )).

fof(redefinition_k2_lattice3,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & lattice(A)
        & latt_str(A) )
     => k2_lattice3(A) = relation_of_lattice(A) ) )).

fof(redefinition_m2_relset_1,axiom,(
    ! [A,B,C] : 
      ( relation_of2_as_subset(C,A,B)
    <=> relation_of2(C,A,B) ) )).

fof(redefinition_r3_lattices,axiom,(
    ! [A,B,C] : 
      ( ( ~ empty_carrier(A)
        & meet_commutative(A)
        & meet_absorbing(A)
        & join_absorbing(A)
        & latt_str(A)
        & element(B,the_carrier(A))
        & element(C,the_carrier(A)) )
     => ( below_refl(A,B,C)
      <=> below(A,B,C) ) ) )).

fof(redefinition_r3_orders_2,axiom,(
    ! [A,B,C] : 
      ( ( ~ empty_carrier(A)
        & reflexive_relstr(A)
        & rel_str(A)
        & element(B,the_carrier(A))
        & element(C,the_carrier(A)) )
     => ( related_reflexive(A,B,C)
      <=> related(A,B,C) ) ) )).

fof(reflexivity_r1_tarski,axiom,(
    ! [A,B] : subset(A,A) )).

fof(reflexivity_r3_lattices,axiom,(
    ! [A,B,C] : 
      ( ( ~ empty_carrier(A)
        & meet_commutative(A)
        & meet_absorbing(A)
        & join_absorbing(A)
        & latt_str(A)
        & element(B,the_carrier(A))
        & element(C,the_carrier(A)) )
     => below_refl(A,B,B) ) )).

fof(reflexivity_r3_orders_2,axiom,(
    ! [A,B,C] : 
      ( ( ~ empty_carrier(A)
        & reflexive_relstr(A)
        & rel_str(A)
        & element(B,the_carrier(A))
        & element(C,the_carrier(A)) )
     => related_reflexive(A,B,B) ) )).

fof(t1_subset,axiom,(
    ! [A,B] : 
      ( in(A,B)
     => element(A,B) ) )).

fof(t2_subset,axiom,(
    ! [A,B] : 
      ( element(A,B)
     => ( empty(B)
        | in(A,B) ) ) )).

fof(t32_filter_1,axiom,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & lattice(A)
        & latt_str(A) )
     => ! [B] : 
          ( element(B,the_carrier(A))
         => ! [C] : 
              ( element(C,the_carrier(A))
             => ( ~ ( in(ordered_pair_as_product_element(the_carrier(A),the_carrier(A),B,C),relation_of_lattice(A))
                    & ~ below_refl(A,B,C) )
                & ~ ( below_refl(A,B,C)
                    & ~ in(ordered_pair_as_product_element(the_carrier(A),the_carrier(A),B,C),relation_of_lattice(A)) ) ) ) ) ) )).

fof(t3_subset,axiom,(
    ! [A,B] : 
      ( element(A,powerset(B))
    <=> subset(A,B) ) )).

fof(t4_subset,axiom,(
    ! [A,B,C] : 
      ( ( in(A,B)
        & element(B,powerset(C)) )
     => element(A,C) ) )).

fof(t5_subset,axiom,(
    ! [A,B,C] : 
      ~ ( in(A,B)
        & element(B,powerset(C))
        & empty(C) ) )).

fof(t6_boole,axiom,(
    ! [A] : 
      ( empty(A)
     => A = empty_set ) )).

fof(t7_boole,axiom,(
    ! [A,B] : 
      ~ ( in(A,B)
        & empty(B) ) )).

fof(t7_lattice3,conjecture,(
    ! [A] : 
      ( ( ~ empty_carrier(A)
        & lattice(A)
        & latt_str(A) )
     => ! [B] : 
          ( element(B,the_carrier(A))
         => ! [C] : 
              ( element(C,the_carrier(A))
             => ( ~ ( below_refl(A,B,C)
                    & ~ related_reflexive(poset_of_lattice(A),cast_to_el_of_LattPOSet(A,B),cast_to_el_of_LattPOSet(A,C)) )
                & ~ ( related_reflexive(poset_of_lattice(A),cast_to_el_of_LattPOSet(A,B),cast_to_el_of_LattPOSet(A,C))
                    & ~ below_refl(A,B,C) ) ) ) ) ) )).

fof(t8_boole,axiom,(
    ! [A,B] : 
      ~ ( empty(A)
        & A != B
        & empty(B) ) )).
%------------------------------------------------------------------------------
