#!/usr/bin/env python3
"""Check of the chloride correction for Cd in step_coast.py against PHREEQC (needs: pip install phreeqpython).

Usage (from the CHemTrace-TW folder):  python dev-tools/tests/cl_check.py
Water: Chianan median groundwater (MOENV WQX_P_02, 94 wells; data/processed/moenv_summary_嘉南平原.md) plus NaCl.
Prints the free-ion fraction from PHREEQC (minteq.v4.dat) relative to chloride-free water, next to the formula F
used by the site. 16 Nov 2026: Cd 0.044 vs 0.051 at 12,350 mg/L; Pb and Ni do not follow the formula (not applied).
"""
import math
from phreeqpython import PhreeqPython
import os
DB=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'phreeqc', 'minteq.v4.dat')
# Chianan groundwater medians (MOENV WQX_P_02, 94 wells): pH 7, Alk 332 mg/L CaCO3, Ca 98.1, Mg 30.8, Na 65.1, K 5.16, SO4 93.6, Cl 42
BETA={'Cd':[1.98,2.6,2.4],'Pb':[1.55,2.2,1.8,1.46],'Ni':[0.408]}
ZC={1:1,2:0,3:1,4:2}   # charge of MCln for a divalent metal
def davies(z,I): return 10**(-0.509*z*z*(math.sqrt(I)/(1+math.sqrt(I))-0.3*I))
def F(m, clmg, I0=0.01):
    c=clmg/35453.0; I=I0+c
    gM, gCl = davies(2,I), davies(1,I)
    s=sum(10**b * gM * gCl**(n+1) / davies(ZC[n+1],I) * c**(n+1) for n,b in enumerate(BETA[m]))
    return 1/(1+s)
pp=PhreeqPython(database=DB)
def free(m, clmg):
    extra=max(0.0, clmg-42.0)/35453.0   # add NaCl on top of the Chianan water
    ip=pp.ip
    inp=f"""SOLUTION 1
 units mg/L
 pH 7.0
 temp 25
 Ca 98.1
 Mg 30.8
 Na {65.1+extra*22990:.3f}
 K 5.16
 Alkalinity 332 as CaCO3
 S(6) 93.6
 Cl {max(clmg,0.0):.3f}
 {m} 1e-6
SELECTED_OUTPUT
 -reset false
 -totals {m}
 -molalities {m}+2
 -ionic_strength true
END"""
    ip.run_string(inp); a=ip.get_selected_output_array()
    h=a[0]; v=a[1]; d=dict(zip(h,v))
    return d[f'm_{m}+2(mol/kgw)']/d[f'{m}(mol/kgw)'], d['mu']
print("metal  Cl mg/L   free frac(PHREEQC)  ratio vs Cl=0 (PHREEQC)   F (formula)   ionic strength")
for m in ('Cd','Pb','Ni'):
    f0,_=free(m,0.0)
    for cl in (0,42,250,1000,5000,12350,19350):
        f,mu=free(m,cl); print(f"{m:3s} {cl:8.0f}  {f:10.3f}   {f/f0:10.3f}   {F(m,cl)/F(m,0):10.3f}   {mu:.3f}")
