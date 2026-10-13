import H1

/-! The axioms behind the main theorems. Every proof is checked by the kernel (`decide +kernel` and
explicit derivations); no `native_decide` is used, so only the standard axioms may appear. -/

#print axioms H1.not_complement_interval
#print axioms H1.L.isCoatom_D
#print axioms H1.L.sdSup
#print axioms H1.L.sdInf
#print axioms H1.L.emb_sup
#print axioms H1.L.emb_inf
#print axioms H1.L.emb_injective
#print axioms H1.K.sdSup
#print axioms H1.K.sdInf
#print axioms H1.L.no_least
