import Lake
open Lake DSL

package H1 where
  leanOptions := #[⟨`autoImplicit, false⟩]

require mathlib from git "https://github.com/leanprover-community/mathlib4" @ "v4.34.1"

/-- the counterexample to the question of Adams, Freese, Nation and Schmid -/
@[default_target]
lean_lib H1
