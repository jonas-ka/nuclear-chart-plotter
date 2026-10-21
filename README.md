# nuclear-chart-plotter

Created for AME16 on 05 November 2019<br/>
Updated to AME20 on 03 October 2024

@author: Jonas Karthein<br/>
@contact: karthein@tamu.edu<br/>
@license: MIT license

### References
[1]: W.J.Huang, Chinese Physics C45, 030002, March 2021.<br/>
[2]: [Linguistics Pro Font (= Utopia Font incl. math symbols)](https://www.fontsquirrel.com/fonts/linguistics-pro)

### Application
The code was used for the dissertation of Jonas Karthein and for several scientific presentations.

### Introduction
The following code was written to provide publication-ready plots of the nuclear chart based on the Atomic Mass Evaluation 2020 [1].

### Required software and libraries
The following code was written in Python 3.11. The required libraries are listed below with a rough description for their task in the code. It doesn't claim to be a full description of the library.

- pandas (data storage and calculation)<br/>
- numpy (calculation)<br/>
- matplotlib (plotting)<br/>
- jupyter (Python notebook environment)<br/>

All packages can be fetched using pip:
`pip3 install pandas numpy matplotlib jupyter`

### Regenerated plots (2026-09-18)
`plots/` contains every figure the notebook produces, exported headless as SVG, PDF and 300 dpi PNG
(Python 3.14, pandas 3, matplotlib 3.10). The notebook was updated on the same date for current
pandas/matplotlib (positional indexing via `.iloc[0]`, scalar annotation coordinates, removed
`InsetPosition` import).

### Laser spectroscopy of radioactive isotopes (2026-10-20)
`bin/laser_spectroscopy_noertershaeuser.csv` lists every radioactive nuclide studied by optical
(laser) spectroscopy, with what was measured, the technique, the facility and the reference. It is
read from the overview table compiled and maintained by the **Nörtershäuser group, Institut für
Kernphysik, TU Darmstadt**: [Laserspektroskopie an radioaktiven Isotopen – Übersicht](https://www.ikp.tu-darmstadt.de/forschung_kernphysik/gruppen_kernphysik/experiment/ag_w_noertershaeuser/forschung_ag_w_noertershaeuser/exotische_kerne_ag_w_noertershaeuser/laserspektroskopie_uebersicht/index.de.jsp)
(on-line experiments published since 1988, continuing E. W. Otten's compilation; the reference
numbers in the CSV point to the bibliography on [their publications page](https://www.ikp.tu-darmstadt.de/forschung_kernphysik/gruppen_kernphysik/experiment/ag_w_noertershaeuser/forschung_ag_w_noertershaeuser/exotische_kerne_ag_w_noertershaeuser/laserspektroskopie_publikationen/index.de.jsp)).
All credit for the compilation goes to them; please cite their page when you use these data.

`uv run bin/laser_spectroscopy_noertershaeuser.py` reads the current page and rewrites the CSV: one
row per nuclide (ground state `g` or isomer `m`, `m1`, ...) and table entry, with `Z`, `A`, `N`,
`state`, `element`, flags for the observables (`I` spin, `mu` magnetic moment, `Q` quadrupole
moment, `dr2` charge-radius change), the `data`, `technique`, `facility` and `reference` columns as
on the page, and the date it was `read`. Compact notation on the page (`6-9, 11`, `116-146 (even)`,
`63, 65, ..., 79`, `68g,m`, `(116, 118) g,m1,m2`) is expanded; entries for molecules (RaF, AcF) and
highly charged ions are listed in `bin/laser_spectroscopy_noertershaeuser_unparsed.txt` and not
expanded. Read on 2026-10-20: 2,409 rows, 1,117 nuclear states of 79
elements.
