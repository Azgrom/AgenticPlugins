# Physical test taxonomy
Read when: assessing organization or proposing file/module moves.

Classify by **evidence kind first, subsystem or API surface second**. `unit`, `interfaces`, `models`
or `macros` alone are not evidence categories. Unit/integration describe test scope as well; retain that
metadata without losing the physical evidence namespaces. Use relevant categories rather than creating
every directory. Existing project rules take precedence; record a concrete conflict and proposed resolution.

| Namespace | Evidence |
| --- | --- |
| examples / vectors | Known input has known result; normative fixture provenance retained |
| conformance | External specification is obeyed; subdivide by standard/revision |
| properties / invariants | General behavioral relationship holds over stated domains |
| differential | Independent implementation/algorithm agrees under defined equivalence |
| interoperability | Independent systems cooperate or communicate correctly |
| adversarial | Hostile/pathological inputs exercise correctness or security contracts |
| invalid / malformed | Illegal states/inputs are rejected as promised |
| boundaries | Limits, degeneracies, numeric extremes |
| regression | A historically observed failure remains fixed |
| integration | Components cooperate across an actual boundary |
| scenarios | A meaningful end-to-end domain story |
| rules | One domain/business rule |
| valid | Accepted programs/documents |
| roundtrip | Forward/reverse transforms preserve semantic meaning |
| diagnostics | Location, message category and recovery diagnostics are correct |
| compatibility | Promised format/version compatibility |
| analytical | Agreement with independently derived mathematics |
| convergence | Approximation approaches the expected solution |
| conditioning | Robustness under ill-conditioning/scaling |
| transitions / sequences | State edges and deliberate histories |
| recovery | Return to valid state after failure |
| reference | Deterministic rendered pixels/samples or other reference results |
| visual | Image comparison under justified pixel/perceptual tolerances |
| scenes | Constructed rendering circumstances |
| corpus | Input data/fixtures, not by itself an executable assertion |
| benchmarks | Performance measurements; only acceptance evidence when tied to a defined contract |

## Domain selection

- Cryptography/general libraries: examples/vectors, conformance, properties, differential, adversarial,
  boundaries, regression, integration, scenarios. Preserve standards/vector versions and policy limits.
- Graphics mathematics: examples/{vector,matrix,quaternion,transforms}; properties for length/angle,
  orthogonality and inverse relationships; differential by oracle; boundaries for zero/near-zero,
  parallel/near-parallel, 180-degree rotations, singularity, magnitude extremes and floating special values;
  conformance by graphics convention/API. State the numeric domain and tolerance contract.
- Business logic: examples, rules, properties, scenarios, invalid, boundaries, regression, integration.
  Checkout/payment/reservation/shipment is a scenario; payment-provider cooperation is integration.
- Standards/protocols: conformance/<standard>/<revision>, interoperability/<peer>, properties, invalid,
  boundaries, regression. Successful communication does not establish standards compliance.
- Parsers/compilers: valid, invalid, conformance, properties, differential, roundtrip, diagnostics,
  regression, corpus. Assert promised recovery and error locations, not rejection alone.
- Serialization: vectors, roundtrip, conformance, compatibility, malformed, boundaries, differential,
  regression. Preserve semantic rather than incidental byte identity unless canonical bytes are promised.
- Numerical algorithms: analytical, properties, convergence, differential, conditioning, boundaries,
  regression, benchmarks. Exact solutions, refinement behavior and numerical robustness are distinct.
- State machines: transitions, properties, sequences, invalid, recovery, regression. Make illegal edges,
  retries, interruption and reconnect/re-entry circumstances visible.
- Rendering: conformance, reference, invariants, scenes, differential, visual, boundaries, regression.
  Image changes need an oracle/tolerance; also test non-image invariants such as depth range or culling.

A test can support several categories; choose one primary physical home and cross-reference obligation
IDs rather than copying the test. Keep interface/generic/macro tests under the kind of evidence they supply,
e.g. properties/macros.rs, invalid/macro_syntax.rs, boundaries/generic_transform.rs.
Compile-pass assertions belong under valid/, compile-fail/rejection under invalid/, and diagnostic
assertions under diagnostics/. Shared compiler input fixtures may live in corpus/; a compile/ test
namespace groups by execution mechanism and loses the evidence distinction.

## Migration and discovery

Record old location → disposition → new category/module → preserved obligation → discovery check.
Preserve fixtures, provenance, visibility needs and distinct regressions when moving tests. Avoid exporting
private APIs solely to fit a directory shape; evidence-category modules can live within a unit-test root.
Tests requiring a different runtime may keep a separate root with the same category organization.

Follow the framework's registration mechanism. In Rust, arbitrary nested integration test files are not
necessarily discovered; use registered root test targets and explicit modules or manifest entries as
appropriate. Keep meaningful private unit contracts within the crate. Compare actual discovered test names
before and after moves, then execute them. File counts and successful builds with zero tests are insufficient.

## One example

For a math library, a useful portion of the layout is:

```text
tests/
  examples/vector.rs
  properties/vector.rs
  properties/frame.rs
  properties/transform.rs
  properties/macros.rs
  boundaries/near_zero.rs
  invalid/macro_syntax.rs
  integration/transform_composition.rs
```

The runner wiring is language/framework-specific and is part of the plan. A straight-line property case
can be one independently named input of a parameterized runner:

```rust
#[test]
fn cross_product_of_basis_x_and_y_is_basis_z() {
    let left = Vec3::X;
    let right = Vec3::Y;
    let result = left.cross(right);
    assert_eq!(result, Vec3::Z);
}
```

This illustrates test form for an existing Vec3 API, not a standalone runnable crate or general proof.
Broader orthogonality laws require their own domains, assertions and case-generation evidence.
