# Physics-Informed Modeling — Equations, Sources, and Rationale

This project was initially built as a purely statistical (black-box)
regression exercise: features in, O/C out, with no representation of the
underlying reactor chemistry. Following review feedback, the pipeline now
encodes actual pyrolysis reaction physics as explicit governing equations
that feed the models, rather than leaving the temperature/composition →
oxygen-content relationship to be inferred purely from correlation. This
document is the full derivation and citation trail for that physics layer
(implemented in `ml/src/physics.py`).

## 1. Reaction kinetics — Independent Parallel Reactions (IPR) model

Lignocellulosic biomass is treated as three independently-decomposing
pseudo-components: **cellulose**, **hemicellulose**, and **lignin** — this
is the standard simplification used throughout the biomass pyrolysis
kinetics literature (e.g. Orfão, Antunes & Figueiredo, *"Pyrolysis
kinetics of lignocellulosic materials — three independent reactions
model"*, Fuel 78(3), 349–358, 1999). Each pseudo-component's thermal
decomposition is modeled as a single first-order Arrhenius reaction:

```
d(alpha_i)/dt = A_i * exp(-Ea_i / (R*T)) * (1 - alpha_i)
```

- `alpha_i` — conversion fraction (0 = undecomposed, 1 = fully decomposed) of pseudo-component *i*
- `A_i` — pre-exponential (frequency) factor [1/s]
- `Ea_i` — activation energy [J/mol]
- `R` — universal gas constant, 8.314 J/(mol·K)
- `T` — instantaneous bed temperature [K]

This is the Arrhenius equation — the fundamental relationship between
temperature and chemical reaction rate — applied to each pseudo-component's
devolatilization reaction.

### Non-isothermal integration (matching real reactor operation)

The dataset's process conditions are a heating rate (`HR`, °C/min) and a
target pyrolysis temperature (`PT`, °C), not an isothermal hold. The
reactor bed temperature rises linearly with time, `T(t) = T0 + beta*t`
(`beta` = heating rate in K/s). Substituting `dt = dT/beta` turns the ODE
above into an integration over temperature instead of time:

```
d(alpha_i)/dT = (A_i/beta) * exp(-Ea_i/(R*T)) * (1 - alpha_i)
```

This is integrated numerically (`scipy.integrate.solve_ivp`, LSODA) from
an ambient starting temperature (25°C / 298.15 K) up to each row's actual
`PT`, at that row's actual `HR` — i.e. the physics is evaluated under the
*exact* process conditions of each experimental row, not a generic curve.
Integrating over temperature rather than wall-clock time is the standard
technique in non-isothermal TGA kinetics analysis; integrating over time
directly is numerically stiff at slow heating rates (the reaction stays
near-zero for a long real-time span, then transitions sharply) and is
what caused an early, since-fixed implementation to hang.

### Kinetic parameters used

Single first-order-reaction (SFOR) kinetic triplets are compiled from
comparative TGA kinetics studies of the three pseudo-components:

| Component | A [1/s] | Ea [kJ/mol] |
|---|---|---|
| Cellulose | 3.50 × 10¹² | 199.66 |
| Hemicellulose | 9.67 × 10⁹ | 95.39 |
| Lignin | 2.59 × 10⁵ | 174.40 |

**Honesty note on these constants:** reported kinetic parameters for the
same pseudo-components vary substantially study-to-study depending on
biomass source, heating rate regime, and fitting method — the pyrolysis
kinetics literature reports cellulose Ea anywhere from ~175–279 kJ/mol,
hemicellulose ~132–186 kJ/mol, lignin ~62–271 kJ/mol (lignin's structure
varies the most between plant species, hence the wide spread). The
triplet above is used as a **physically-motivated prior** — internally
consistent (all three values come from one matched comparative-kinetics
source, so the A/Ea pairing is not mismatched across studies) — not a
value fitted to this project's own dataset. Cellulose kinetics
specifically are also cross-checked against the classic Broido-Shafizadeh
three-reaction scheme (Bradbury, Sakai & Shafizadeh, *"A kinetic model
for pyrolysis of cellulose"*, J. Applied Polymer Science 23, 3271–3280,
1979), which reports comparable activation energies (153–243 kJ/mol
across its three sub-reactions) for the same decomposition process.

### Derived features fed into the models

- `physics_alpha_cellulose`, `physics_alpha_hemicellulose`, `physics_alpha_lignin` — predicted conversion fraction of each pseudo-component at that row's actual PT/HR
- `physics_conversion` — composition-weighted overall conversion: `(Cel%·alpha_cel + Hem%·alpha_hem + Lig%·alpha_lig) / (Cel%+Hem%+Lig%)`
- `physics_char_fraction` = `1 − physics_conversion` — a mechanistic proxy for how much of the feedstock stayed solid (char) rather than devolatilizing into vapor/oil

## 2. Modified Dulong formula — fuel energy content

A standard combustion-engineering correlation estimating a solid fuel's
higher heating value (HHV, MJ/kg) directly from its ultimate (elemental)
analysis:

```
HHV = 33.5*C + 142.3*H - 15.4*O - 14.5*N
```

where C, H, O, N are mass fractions (0–1) of carbon, hydrogen, oxygen,
and nitrogen. This gives the models a physics-derived estimate of the
feedstock's own energy content (`physics_hhv_dulong`) as an input feature
— directly relevant to the calorific-value target, and to O/C, since both
track how oxygen-loaded the feedstock is to begin with.

## 3. Why this matters: physics-only vs. ML-only vs. hybrid

To make the value of the physics layer explicit (not just asserted), three
things are compared on the same held-out test set, all reported in
`ml/reports/benchmark_results.md` / `physics_baseline.json`:

1. **Physics-only baseline** — a single linear regression using *only*
   `physics_char_fraction` and the feedstock's own O/C ratio, with none of
   the other 12+ statistical features. This isolates what the governing
   equations alone can explain.
2. **Pure-ML (previous iteration)** — the original tree/linear/GPR models
   trained without any physics features, using only raw composition and
   process-condition columns plus simple ratios.
3. **Hybrid physics + ML (current)** — the same model family, now with the
   physics-derived features (`physics_alpha_*`, `physics_conversion`,
   `physics_char_fraction`, `physics_hhv_dulong`) included alongside the
   statistical features.

The hybrid approach improved test-set accuracy over the pure-ML baseline
for the tree ensembles (Random Forest test R² rose from 0.836 to 0.887;
XGBoost from 0.886 to 0.891 — see `benchmark_results.md` for the full,
re-run comparison) — i.e. the reactor physics is not just present for
explanatory value, it measurably helps the model generalize.

## 4. What this is *not*

This is a **hybrid grey-box model** — physics-derived features feeding a
statistical learner — not a full physics-informed neural network (PINN)
with the governing PDEs enforced as a soft constraint on the loss
function, and not a full computational reactor simulation (no heat/mass
transfer within the particle, no secondary vapor-phase cracking
reactions, no reactor-scale fluid dynamics). Given the dataset size
(~230 usable rows) and the project's scope, a full PINN or CFD-coupled
model would add substantial complexity without a correspondingly large
benefit — the brief this project follows explicitly called for skipping
that route unless there was a clean way to encode kinetics as a
constraint. This physics layer is that clean way: real governing
equations, literature-sourced constants, integrated under each row's
actual process conditions, feeding — not replacing — the trained model.
