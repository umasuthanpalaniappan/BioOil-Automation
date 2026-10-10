"""Shared physics features. Inputs needed: C, H, O, N (wt%), T (deg C), HR (deg C/min), PS (mm)."""
import numpy as np, pandas as pd
R = 8.314            # J/mol/K
ALPHA = 1.0e-7       # thermal diffusivity of biomass, m2/s

def kinetics(T):
    """Chan et al. (1985) wood scheme: wood -> gas / tar / char (rates in 1/s)."""
    TK = np.asarray(T, float) + 273.15
    kg = 1.43e4 * np.exp(-88.6e3 / (R * TK))
    kt = 4.13e6 * np.exp(-112.7e3 / (R * TK))
    kc = 7.38e5 * np.exp(-106.5e3 / (R * TK))
    return kg, kt, kc

def add_features(df):
    f = df.copy()
    f['feed_OC'] = (f['O'] / 16) / (f['C'] / 12)                      # molar O/C of biomass
    f['feed_HC'] = (f['H'] / 1.008) / (f['C'] / 12)                   # molar H/C of biomass
    f['feed_HCeff'] = (f['H'] / 1.008 - 2 * f['O'] / 16) / (f['C'] / 12)  # H left after O forms water
    f['logHR'] = np.log10(f['HR'])
    f['logPS'] = np.log10(f['PS'])
    t_cond = (f['PS'] / 2 / 1000) ** 2 / ALPHA                         # heat soaks into particle, s
    t_heat = (f['T'] - 25) / f['HR'] * 60                              # reactor reaches final T, s
    f['log_theta'] = np.log10(t_cond / t_heat)                         # heating regime
    kg, kt, kc = kinetics(f['T'])
    f['S_tar'] = kt / (kg + kt + kc)                                   # kinetic share to liquid
    f['log_Py'] = np.log10((1 / (kg + kt + kc)) / t_cond)              # pyrolysis number
    f['logTSI'] = np.log10(f['T'] * np.log(f['HR'] + 1) / f['PS'])     # thermal severity index
    return f

RAW = ['C', 'H', 'O', 'N', 'T', 'HR', 'PS']
PHYS = ['feed_OC', 'feed_HC', 'feed_HCeff', 'N', 'T', 'logHR', 'logPS', 'log_theta', 'S_tar', 'log_Py', 'logTSI']
