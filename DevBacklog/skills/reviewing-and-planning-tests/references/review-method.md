# Review method
Read when: inspecting test adequacy and designing cases or assertions.

## Inventory and baseline

Identify projects from build/workspace manifests, solution files, repository layout and CI. Include
excluded packages, independent test projects and separately built/deployed applications; a virtual
workspace manifest alone is not another project. Record ownership for shared harnesses and integration
boundaries. Inspect every project's relevant nested instructions and declared constraints.

For each project record:
- Actual source/test locations, framework, registration, runner entry points and category layout.
- Public contracts and independently meaningful internal contracts; implemented versus placeholder APIs.
- Default versus full-solution commands, CI differences, features, profiles, target/runtime variants,
  generated/compile-time tests, ignored/quarantined tests and fixtures requiring external resources.
- Observed commands/results with artifact identity; inherited failures separate from new findings.
- Existing standards, vectors, issue regressions, domain rules, test tooling and trustworthy reuse options.

A file's existence does not establish that it runs. Compare registered/discovered tests with source files.
Run appropriate baselines when available; preserve exact reasons for unavailable environments or costly
checks deferred by scope. Never label an unrun command passing. Record relevant dirty changes with the
source revision so evidence cannot silently attach to a different artifact.

## Obligation graph

Each obligation has an ID, authoritative source/revision, domain, preconditions, property/postcondition,
independent oracle or evidence method, applicable configurations, current tests, gaps, owning project and
acceptance check. Label interpretations and unresolved requirements explicitly. Seek authoritative primary
sources for correctness-sensitive claims; specification vectors outrank invented expected values.

For a primitive, translate its intended abstraction into laws. Examples include closure, identity,
associativity, inverses, distributivity, dimensional compatibility and valid representation. Apply only
laws that the actual contract promises. A vector-space claim needs its scalar field/domain and operations;
basis membership also needs dimensionality, spanning/independence conditions and a reconstruction criterion.
A few familiar examples do not discharge those obligations.

For numerical implementations, separate ideal mathematics from finite arithmetic: rounding, overflow,
NaN/infinity/signed zero, singularity and conditioning may restrict or change a law. Define meaningful
absolute/relative/error-budget comparisons and their sources; arbitrary loose tolerances hide failures.
Real-number associativity is not automatically a floating-point contract.

Traverse composed types to arbitrary depth. Give shared types stable nodes; record recursive references
as graph edges rather than expanding indefinitely. For each parent obligation, name the child obligations
and contextual assumptions it relies on. Review children before crediting dependent parent evidence.

Child tests alone do not establish the parent contract. Exercise composed operations in contexts where
child assumptions hold, at their boundaries, and where they fail. Assert integrated outcomes and rejection
or containment promised by the parent. A parent property remains unsupported when a required constituent
property is unestablished in that circumstance, even if a happy-path parent example passes.

Evidence labels:
- **Sampled:** selected or generated inputs; record ranges, seeds, distributions and counterexamples.
- **Exhaustive finite-domain:** enumerate the defined finite domain/configuration and account for every
  case; distinguish all values from representative equivalence classes.
- **Formal proof:** identify the proof artifact, model, assumptions and relationship to the implementation.

Passing sampled properties is evidence, not universal proof. Even exhaustive finite transition checks need
explicit state-observation/model assumptions before supporting claims about arbitrary histories.

## Operation and surface matrices

Map pre-state/input class × operation × relevant configuration × outcome. Include ordinary and unusual
valid use, boundaries, invalid/hostile cases, repeated operations, order-sensitive combinations, resource
limits, partial failures, recovery and regressions. Bound stateful exploration by justified state classes
or sequence depths; record omitted combinations and their consequences. Cover meaningful interactions,
not an unbounded Cartesian product disguised as exhaustive testing.

| Surface | Required specialization |
| --- | --- |
| Primitive/complex types | Constructor and representation contracts, laws, lifecycle and composed operations |
| Interfaces/traits | Contract shared by implementations, substitutability, dispatch/default behavior and rejection semantics |
| Static/free functions | Input partitions, determinism/purity promises, errors, environmental assumptions and composition |
| Generic functions/types | Meaningful type/const/feature classes, constraint boundaries and discriminating witnesses; one instantiation is not universal evidence |
| Macros | Accepted/rejected syntax, expansion behavior, hygiene/name resolution, argument evaluation and compile-time diagnostics where promised |

Compile-pass/fail tests and diagnostics checks are separate from runtime source coverage. Source expansion
coverage does not establish all generic or macro behavior. Cover downstream use where the contract crosses
a package boundary. Avoid duplicating compiler guarantees without an independent project contract.

For stateful operations, assert both result and resulting state, including unchanged state on rejection
when promised. Observe intermediate invariants in deliberate scenarios. For pure functions, arrange inputs,
act to obtain a result and assert it; for compile-time tests, arrange the consumer fixture, compile, then
assert acceptance or the relevant diagnostic. No artificial state mutation is needed.

## Repetition, independence and minimization

Keep individual tests straight-line and diagnostic. Prefer named parameterized cases or property-runner
callbacks; record seed/shrinking or deterministic replay information. The runner may repeat cases outside
test bodies. An explicit test-body loop is allowed only when the tested behavior cannot reasonably be
expressed without it, such as an algorithm's convergence trace; record why, bounded termination and failure
identification. Convenience, avoiding several test names or generating an ordinary input table is not
necessity. Moving that loop into a helper solely to evade the rule is still the same design defect.

Use standards, analytical solutions, independent algorithms/implementations or externally sourced fixtures
as oracles. Self-roundtrip establishes a relation, not external correctness. Differential agreement is not
conformance when both implementations share a defect. Preserve provenance, precision and normalization
assumptions. An external differential crate/process can isolate dependencies only when policy permits it;
project-wide restrictions still apply. Plan a dependency-free oracle, approved fixture generation or a
blocked approval task when appropriate.

A case matrix maps each test to obligations, input/sequence classes and measured coverage contributions.
Consolidate equivalent cases and remove tests only when their distinct evidence, regression purpose and
diagnostic value remain covered. Describe the practical minimization rationale; do not assert a globally
minimum suite without establishing it. A giant test with many unrelated assertions is not a useful minimum.

## Coverage and review verdict

Declare the coverage denominator, source scope, tool/version, measurement kind, configurations and exclusions.
Target 100% reachable statements and branches per declared scope, with an aggregate view where appropriate.
Track uncovered reachable code separately from proven unreachable, generated, platform-specific or
unmeasurable code. Justify every disposition; do not remove reachable code from the denominator to meet a
percentage. Line/region/function coverage cannot silently substitute for statement/branch measurement.

Report unavailable instrumentation as missing evidence with a bounded tooling task. State zero-denominator
cases explicitly. Numeric coverage cannot establish assertion strength, all paths through loops, all
operation histories, generic contracts or external correctness. Continue property/contract work after
coverage saturates. Use targeted fault injection or mutation checks when assertion effectiveness is in
question; record what they establish without making additional tooling a universal dependency.

For each important user failure—wrong results, corruption, crashes, unusable state, misleading diagnostics,
recovery failure, incompatibility or promised resource/security behavior—identify the category expected to
expose it. Where no credible category exists, record a missing class or a design limitation.

Treat disproportionate mocking, hidden mutable/global state, implicit dependencies, unclear ownership,
ambiguous preconditions/errors, uncontrollable nondeterminism or invasive access as interface findings.
Describe impact and a testable seam or contract clarification; do not silently patch production under a
review request. Prefer observable behavior. Test internals directly when they have their own meaningful
contract or necessary evidence unavailable through public behavior.

Preserve significant defects as contract-focused regression tests with issue/circumstance provenance.
Conclude each project report with evidence established, evidence missing, interface findings and limits.
Prioritize by impact/dependencies/maturity, not test count. A placeholder may need a contract-definition
step; it cannot earn conformance evidence merely because it has no executable statements.
