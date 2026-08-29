"""Pyrolysis reaction physics used as engineered features for the ML models.

This module encodes actual reactor chemistry — reaction kinetics and a
combustion-engineering energy correlation — as explicit equations, rather
than leaving the model to infer everything statistically from correlations.
The intent (per project review feedback): the model should be told *how the
process works* via governing equations, and only then be trained/tuned on
top of that physical structure ("physics-informed" / hybrid grey-box ML,
not a purely black-box regressor).

-------------------------------------------------------------------------
1) Independent Parallel Reactions (IPR) pyrolysis kinetics
-------------------------------------------------------------------------
Lignocellulosic biomass is treated as three independently-reacting
pseudo-components — cellulose, hemicellulose, lignin — each following a
single first-order Arrhenius reaction (the standard IPR framework used in
biomass pyrolysis kinetics literature, e.g. Orfao, Antunes & Figueiredo,
"Pyrolysis kinetics of lignocellulosic materials - three independent
reactions model", Fuel 78(3), 1999):

    d(alpha_i)/dt = A_i * exp(-Ea_i / (R*T)) * (1 - alpha_i)

  alpha_i(t)  : conversion fraction (0-1) of pseudo-component i at time t
  A_i         : pre-exponential (frequency) factor [1/s]
  Ea_i        : activation energy [J/mol]
  R           : universal gas constant, 8.314 J/(mol*K)
  T           : instantaneous temperature [K]

For a reactor heated at a constant rate HR [deg C/min] from an ambient
starting temperature T0 up to the process temperature PT, temperature
rises linearly with time: T(t) = T0 + HR*t. Integrating the ODE above
from t=0 to the time the bed reaches PT gives the conversion fraction
predicted by reaction kinetics alone for that pseudo-component, under
those exact process conditions — this is a genuine physics computation,
not a fitted statistical feature.

Kinetic triplets (A, Ea) used below are literature-representative single
first-order-reaction (SFOR) values compiled from comparative TGA kinetics
studies of the three pseudo-components (see ml/reports/physics.md for the
full citation and the wide range reported study-to-study — these are used
as physically-motivated priors, not values fitted to this project's
dataset).

-------------------------------------------------------------------------
2) Modified Dulong formula (fuel higher heating value)
-------------------------------------------------------------------------
Standard solid-fuel combustion-engineering correlation estimating higher
heating value (HHV, MJ/kg) directly from a fuel's ultimate (elemental)
analysis:

    HHV = 33.5*C + 142.3*H - 15.4*O - 14.5*N

  C, H, O, N  : mass fractions (0-1) of carbon, hydrogen, oxygen, nitrogen

This gives the models a physics-derived estimate of the feedstock's own
energy content as an input feature, directly relevant to the calorific
value target and to O/C (both track feedstock oxygen loading).

-------------------------------------------------------------------------
3) Broido-Shafizadeh competitive cellulose pathway (Bradbury, Sakai &
   Shafizadeh, 1979, J. Applied Polymer Science 23, 3271-3280)
-------------------------------------------------------------------------
The single first-order reaction used for cellulose above (Section 1) is
a lumped simplification. Cellulose pyrolysis is more accurately a
three-reaction competitive scheme: cellulose first forms an intermediate
"active cellulose", which then splits along TWO competing pathways —
one to oxygenated volatiles (chiefly levoglucosan), the other to char
plus light gas:

    Cellulose --ki--> Active Cellulose
    Active Cellulose --kv--> Volatiles (oxygenated tar/oil precursors)
    Active Cellulose --kc--> Char + Gas

    ki = 1.7e21 * exp(-242,672/RT)  1/min
    kv = 1.9e16 * exp(-197,905/RT)  1/min
    kc = 7.9e11 * exp(-153,134/RT)  1/min

(Original source reports Ea in cal/mol: 58,000 / 47,300 / 36,600
cal/mol for ki/kv/kc; converted to J/mol above at 4.184 J/cal.) This is
integrated the same non-isothermal way as Section 1, over the same T0-to-PT
span, giving a *cellulose-specific* predicted split between oxygenated
volatile products and char+gas — a genuinely competitive-pathway feature,
not a single lumped conversion number.

-------------------------------------------------------------------------
4) Secondary vapor-phase tar-cracking severity
-------------------------------------------------------------------------
Primary pyrolysis vapors (oxygenated tars) can undergo further
gas-phase "secondary cracking" reactions at high temperature, breaking
larger oxygenated molecules into lighter gases and losing oxygen along
the way — this is the actual chemical mechanism behind the well-known
empirical pattern "higher PT -> lower bio-oil O/C." A first-order
Arrhenius rate for this secondary reaction (kinetic triplet commonly
attributed to Liden, Berruti & Scott, 1988) is evaluated at each row's
process temperature and combined with a residence-time proxy (time
spent at/near PT, approximated from HR) into a dimensionless cracking
severity index: severity = k(PT) * t_residence.

    k(T) = 4.28e6 * exp(-107,500/RT)   1/s

**Confidence caveat:** this specific triplet is very widely cited across
reactor-modeling papers as "Liden et al. 1988", but this project's
sandboxed environment could not fetch the primary source to verify the
figures word-for-word against the original thesis/paper. It is used here
as a literature-representative order-of-magnitude value for secondary
cracking severity, not a value fitted to this dataset — treat the
resulting feature as directionally meaningful (it correctly increases
with PT and residence time, which is the qualitatively correct behavior)
rather than a precisely validated rate constant.

-------------------------------------------------------------------------
5) Ash-catalyzed devolatilization (alkali/alkaline-earth catalytic effect)
-------------------------------------------------------------------------
Biomass ash is rich in alkali and alkaline-earth metals (K, Na, Ca, Mg)
which are well documented in the pyrolysis literature to catalytically
lower cellulose's effective activation energy, accelerating dehydration
reactions and shifting product distribution away from levoglucosan and
toward char + light oxygenated fragments. This is modeled as a simple,
explicitly-approximate linear correction to the cellulose activation
energy used in Section 1:

    Ea_effective = Ea_cellulose * (1 - k_ash * Ash_fraction)

with a modest literature-informed coefficient k_ash = 0.3 (i.e. an
ash-saturated feedstock could plausibly see up to ~30% Ea reduction,
consistent with the qualitative direction and rough magnitude reported
for alkali-catalyzed cellulose decomposition, though exact catalytic
strength depends on which specific minerals are present, which this
dataset does not resolve). This is the most approximate feature in this
module — kept because the qualitative catalytic effect is real and
well-established, even though the exact coefficient is a reasoned
estimate rather than a value from one specific calibrated study.
"""
import numpy as np
from scipy.integrate import solve_ivp

R_GAS = 8.314  # J / (mol K)
T0_AMBIENT_K = 298.15  # 25 C, reactor/feed starting temperature

# Broido-Shafizadeh competitive cellulose scheme (Bradbury, Sakai & Shafizadeh 1979).
# A in 1/min; Ea in J/mol (converted from the original cal/mol at 4.184 J/cal).
BROIDO_SHAFIZADEH = {
    "ki": {"A": 1.7e21, "Ea": 58_000 * 4.184},   # cellulose -> active cellulose
    "kv": {"A": 1.9e16, "Ea": 47_300 * 4.184},   # active cellulose -> volatiles
    "kc": {"A": 7.9e11, "Ea": 36_600 * 4.184},   # active cellulose -> char + gas
}

# Secondary tar-cracking kinetic triplet (Liden, Berruti & Scott 1988,
# as widely cited in reactor-modeling literature; see confidence caveat above).
TAR_CRACKING = {"A": 4.28e6, "Ea": 107_500.0}  # 1/s, J/mol

ASH_CATALYSIS_COEFFICIENT = 0.3  # fractional Ea reduction at Ash_fraction = 1.0

# Single first-order-reaction (SFOR) kinetic triplets, literature-representative.
# See ml/reports/physics.md for citations and reported ranges.
KINETIC_PARAMS = {
    "cellulose":     {"A": 3.50e12, "Ea": 199_660.0},  # A [1/s], Ea [J/mol]
    "hemicellulose": {"A": 9.67e9,  "Ea": 95_390.0},
    "lignin":        {"A": 2.59e5,  "Ea": 174_400.0},
}


def _conversion_fraction(A: float, Ea: float, pt_celsius: float, hr_c_per_min: float) -> float:
    """Integrate the first-order Arrhenius conversion ODE from T0 to PT at
    heating rate HR, and return the predicted conversion fraction (0-1)
    reached by the time the bed hits the process temperature.

    Standard non-isothermal-kinetics technique: change the integration
    variable from time to temperature (dT/dt = beta = const heating rate),
    so d(alpha)/dT = (A/beta) * exp(-Ea/RT) * (1-alpha). Integrating over
    the ~500 K temperature span is well-conditioned; integrating the same
    ODE over real wall-clock seconds at slow heating rates spans many
    thousands of seconds with a sharp late-stage transition and is
    numerically stiff for an explicit solver.
    """
    if pt_celsius is None or hr_c_per_min is None:
        return np.nan
    if np.isnan(pt_celsius) or np.isnan(hr_c_per_min) or hr_c_per_min <= 0:
        return np.nan
    pt_k = pt_celsius + 273.15
    if pt_k <= T0_AMBIENT_K:
        return 0.0

    beta_k_per_s = hr_c_per_min / 60.0  # heating rate, K/s

    def rhs(T, alpha):
        a = min(max(alpha[0], 0.0), 1.0)
        k = A * np.exp(-Ea / (R_GAS * T))
        return [(k / beta_k_per_s) * (1.0 - a)]

    sol = solve_ivp(rhs, [T0_AMBIENT_K, pt_k], [0.0], method="LSODA", rtol=1e-6, atol=1e-9)
    alpha_final = float(sol.y[0, -1])
    return min(max(alpha_final, 0.0), 1.0)


def kinetic_conversion_features(cel_pct, hem_pct, lig_pct, pt_celsius, hr_c_per_min) -> dict:
    """Physics-predicted conversion of each pseudo-component and the
    composition-weighted overall conversion / char-fraction proxy.
    """
    out = {}
    for name, params in KINETIC_PARAMS.items():
        out[f"physics_alpha_{name}"] = _conversion_fraction(params["A"], params["Ea"], pt_celsius, hr_c_per_min)

    fracs = {"cellulose": cel_pct, "hemicellulose": hem_pct, "lignin": lig_pct}
    total = sum(v for v in fracs.values() if v is not None and not np.isnan(v))
    if total and total > 0:
        weighted = sum(
            (fracs[name] / total) * out[f"physics_alpha_{name}"]
            for name in KINETIC_PARAMS
            if fracs[name] is not None and not np.isnan(fracs[name]) and not np.isnan(out[f"physics_alpha_{name}"])
        )
        out["physics_conversion"] = weighted
        out["physics_char_fraction"] = 1.0 - weighted
    else:
        out["physics_conversion"] = np.nan
        out["physics_char_fraction"] = np.nan
    return out


def _residence_time_s(pt_celsius: float, hr_c_per_min: float) -> float:
    """Time (seconds) for the bed to rise from T0 to PT at heating rate HR —
    used as a proxy for vapor residence time near the process temperature."""
    if pt_celsius is None or hr_c_per_min is None:
        return np.nan
    if np.isnan(pt_celsius) or np.isnan(hr_c_per_min) or hr_c_per_min <= 0:
        return np.nan
    pt_k = pt_celsius + 273.15
    if pt_k <= T0_AMBIENT_K:
        return 0.0
    beta_k_per_s = hr_c_per_min / 60.0
    return (pt_k - T0_AMBIENT_K) / beta_k_per_s


def broido_shafizadeh_cellulose(pt_celsius: float, hr_c_per_min: float) -> dict:
    """Integrate the competitive 3-reaction cellulose scheme (Section 3) from
    T0 to PT at heating rate HR (native units: HR is already deg C/min, which
    equals K/min, so this integrates directly in minutes — no unit conversion
    needed, unlike the SFOR triplets which use per-second rate constants).
    Returns cellulose-specific volatile-fraction and char+gas-fraction.
    """
    if pt_celsius is None or hr_c_per_min is None:
        return {"physics_cellulose_volatile_fraction": np.nan, "physics_cellulose_chargas_fraction": np.nan}
    if np.isnan(pt_celsius) or np.isnan(hr_c_per_min) or hr_c_per_min <= 0:
        return {"physics_cellulose_volatile_fraction": np.nan, "physics_cellulose_chargas_fraction": np.nan}
    pt_k = pt_celsius + 273.15
    if pt_k <= T0_AMBIENT_K:
        return {"physics_cellulose_volatile_fraction": 0.0, "physics_cellulose_chargas_fraction": 0.0}

    beta_k_per_min = hr_c_per_min  # deg C/min == K/min

    def rhs(T, y):
        C, AC, V, CG = y
        C, AC = max(C, 0.0), max(AC, 0.0)
        ki = BROIDO_SHAFIZADEH["ki"]["A"] * np.exp(-BROIDO_SHAFIZADEH["ki"]["Ea"] / (R_GAS * T))
        kv = BROIDO_SHAFIZADEH["kv"]["A"] * np.exp(-BROIDO_SHAFIZADEH["kv"]["Ea"] / (R_GAS * T))
        kc = BROIDO_SHAFIZADEH["kc"]["A"] * np.exp(-BROIDO_SHAFIZADEH["kc"]["Ea"] / (R_GAS * T))
        dC = -ki * C
        dAC = ki * C - (kv + kc) * AC
        dV = kv * AC
        dCG = kc * AC
        return [dC / beta_k_per_min, dAC / beta_k_per_min, dV / beta_k_per_min, dCG / beta_k_per_min]

    sol = solve_ivp(rhs, [T0_AMBIENT_K, pt_k], [1.0, 0.0, 0.0, 0.0], method="LSODA", rtol=1e-6, atol=1e-9)
    V_final, CG_final = float(sol.y[2, -1]), float(sol.y[3, -1])
    return {
        "physics_cellulose_volatile_fraction": min(max(V_final, 0.0), 1.0),
        "physics_cellulose_chargas_fraction": min(max(CG_final, 0.0), 1.0),
    }


def tar_cracking_severity(pt_celsius: float, hr_c_per_min: float) -> float:
    """Dimensionless secondary-cracking severity index: k(PT) * residence_time.
    Larger values mean more secondary deoxygenation of primary vapors."""
    t_res = _residence_time_s(pt_celsius, hr_c_per_min)
    if np.isnan(t_res):
        return np.nan
    pt_k = pt_celsius + 273.15
    k = TAR_CRACKING["A"] * np.exp(-TAR_CRACKING["Ea"] / (R_GAS * pt_k))
    return k * t_res


def ash_catalyzed_cellulose_conversion(pt_celsius, hr_c_per_min, ash_pct) -> float:
    """Cellulose SFOR conversion (Section 1) with an ash-catalysis correction
    to the activation energy (Section 5)."""
    if ash_pct is None or (isinstance(ash_pct, float) and np.isnan(ash_pct)):
        return np.nan
    ash_frac = min(max(ash_pct / 100.0, 0.0), 1.0)
    base = KINETIC_PARAMS["cellulose"]
    ea_eff = base["Ea"] * (1.0 - ASH_CATALYSIS_COEFFICIENT * ash_frac)
    return _conversion_fraction(base["A"], ea_eff, pt_celsius, hr_c_per_min)


def dulong_hhv(c_pct, h_pct, o_pct, n_pct) -> float:
    """Modified Dulong formula: HHV (MJ/kg) from ultimate analysis mass %."""
    if any(v is None or (isinstance(v, float) and np.isnan(v)) for v in (c_pct, h_pct, o_pct, n_pct)):
        return np.nan
    C, H, O, N = c_pct / 100.0, h_pct / 100.0, o_pct / 100.0, n_pct / 100.0
    return 33.5 * C + 142.3 * H - 15.4 * O - 14.5 * N


def physics_features_for_row(row: dict) -> dict:
    """Compute all physics-informed features for one feedstock/condition row.
    `row` must have keys: Cel, Hem, Lig, VM, Ash, C%, H%, O%, N%, PT, HR (raw, un-prefixed).
    """
    pt, hr, ash = row.get("PT"), row.get("HR"), row.get("Ash")

    feats = kinetic_conversion_features(row.get("Cel"), row.get("Hem"), row.get("Lig"), pt, hr)
    feats["physics_hhv_dulong"] = dulong_hhv(row.get("C%"), row.get("H%"), row.get("O%"), row.get("N%"))
    feats.update(broido_shafizadeh_cellulose(pt, hr))
    feats["physics_tar_cracking_severity"] = tar_cracking_severity(pt, hr)
    feats["physics_alpha_cellulose_ash_adjusted"] = ash_catalyzed_cellulose_conversion(pt, hr, ash)
    feats["physics_residence_time_s"] = _residence_time_s(pt, hr)
    return feats


PHYSICS_FEATURE_COLS = [
    "physics_alpha_cellulose", "physics_alpha_hemicellulose", "physics_alpha_lignin",
    "physics_conversion", "physics_char_fraction", "physics_hhv_dulong",
    "physics_cellulose_volatile_fraction", "physics_cellulose_chargas_fraction",
    "physics_tar_cracking_severity", "physics_alpha_cellulose_ash_adjusted",
    "physics_residence_time_s",
]
