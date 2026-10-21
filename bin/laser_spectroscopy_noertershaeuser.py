# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4", "pandas"]
# ///
"""Laser spectroscopy of radioactive isotopes, from the overview table of the Nörtershäuser group.

    uv run bin/laser_spectroscopy_noertershaeuser.py      # writes bin/laser_spectroscopy_noertershaeuser.csv

Source: W. Nörtershäuser group, Institut für Kernphysik, TU Darmstadt, "Laserspektroskopie an
radioaktiven Isotopen – Übersicht", https://www.ikp.tu-darmstadt.de/forschung_kernphysik/gruppen_kernphysik/experiment/ag_w_noertershaeuser/forschung_ag_w_noertershaeuser/exotische_kerne_ag_w_noertershaeuser/laserspektroskopie_uebersicht/index.de.jsp
(table "Tabelle der Nuklide": on-line optical spectroscopy of radionuclides published since January
1988, continuing E. W. Otten, Treatise on Heavy-Ion Science 8 (1989); references and abbreviations
on that page). All credit for the compilation goes to them; this script only reads it.

One row per nuclide and table entry: Z, A, state (g for the ground state, m, m1, m2, ... for
isomers, as written), element, the observables (I spin, mu magnetic moment, Q quadrupole moment,
dr2 change in mean-square charge radius, other), technique, facility and reference as on the page,
and the date the page was read. Entries the parser cannot expand are listed in
bin/laser_spectroscopy_noertershaeuser_unparsed.txt for a manual check.
"""

import datetime as dt
import re
import urllib.request
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

URL = ("https://www.ikp.tu-darmstadt.de/forschung_kernphysik/gruppen_kernphysik/experiment/ag_w_noertershaeuser/"
       "forschung_ag_w_noertershaeuser/exotische_kerne_ag_w_noertershaeuser/laserspektroskopie_uebersicht/index.de.jsp")
BIN = Path(__file__).resolve().parent
OUT = BIN / "laser_spectroscopy_noertershaeuser.csv"
UNPARSED = BIN / "laser_spectroscopy_noertershaeuser_unparsed.txt"


def cell_text(td) -> str:
    for br in td.find_all("br"):
        br.replace_with(", ")
    t = td.get_text("", strip=False).replace("\u2013", "-").replace("\u2212", "-").replace("\u2026", "...")
    return re.sub(r"\s+", " ", t).strip(" ,")


def rows(html: str) -> list[list[str]]:
    """The table body as a grid, with rowspans filled in."""
    table = BeautifulSoup(html, "html.parser").find("table", id="tabelle_nuklidtabelle")
    out, pending = [], {}            # column -> (text, rows left)
    for tr in table.find("tbody").find_all("tr", recursive=False):
        cells, col, tds = [], 0, tr.find_all(["td", "th"], recursive=False)
        while tds or col in pending:
            if col in pending:
                text, left = pending[col]
                cells.append(text)
                pending[col] = (text, left - 1)
                if left - 1 == 0:
                    del pending[col]
            else:
                td = tds.pop(0)
                text = cell_text(td)
                cells.append(text)
                span = int(td.get("rowspan", 1))
                if span > 1:
                    pending[col] = (text, span - 1)
            col += 1
        out.append(cells)
    return out


def expand(spec: str) -> list[tuple[int, str]] | None:
    """'6-9, 11' / '116-146 (even)' / '63, 65, ..., 79' / '68g,m; 70g,m1,m2' / '(116, 118) g,m1' /
    '190g,m-192g,m' / '197-198m' / '176ls,hs' -> [(A, state)]."""
    s = spec.replace(";", ",")
    even = odd = False
    if "(even)" in s:
        even, s = True, s.replace("(even)", "")
    if "(odd)" in s:
        odd, s = True, s.replace("(odd)", "")
    # '(116, 118, 120) g,m1,m2': every A in the group with every state
    m = re.search(r"\(([\d,\s]+)\)\s*((?:g|m\d?)(?:\s*,\s*(?:g|m\d?))*)", s)
    if m:
        group = ",".join(f"{a.strip()}{st.strip()}" for a in m[1].split(",") for st in m[2].split(","))
        s = s[:m.start()] + group + s[m.end():]
    s = re.sub(r"(\d)\s+(?=\d)", r"\1,", s)          # '98m1 98m2' -> two items
    s = s.replace(" ", "")
    s = re.sub(r"(\d+)g,m-(\d+)g,m", lambda q: ",".join(f"{a}{st}" for a in range(int(q[1]), int(q[2]) + 1) for st in "gm"), s)
    s = re.sub(r"\.{3,}", "...,", s)
    items = [x for x in s.split(",") if x]
    out, last_a, gap = [], None, set()
    for it in items:
        if it == "...":
            gap = {"g", "m"}
            continue
        m = re.fullmatch(r"(\d+)-(\d+)(m\d?)?", it)
        if m:
            a0, a1, st = int(m[1]), int(m[2]), m[3] or "g"
            out += [(a, st) for a in range(a0, a1 + 1) if not (even and a % 2) and not (odd and a % 2 == 0)]
            last_a = a1
            continue
        m = re.fullmatch(r"(\d+)m-(\d+)m", it)
        if m:
            out += [(a, "m") for a in range(int(m[1]), int(m[2]) + 1)]
            continue
        m = re.fullmatch(r"(\d+)(g|m\d?|ls|hs|s|f)?", it)
        if m:
            a, st = int(m[1]), m[2] or "g"
            series = st if st in ("g", "m") else None
            if series in gap:        # '63, 65, 67, ..., 79': continue the series with its step
                prev = [x for x, y in out if y == series]
                if len(prev) >= 2:
                    step = prev[-1] - prev[-2]
                    out += [(x, series) for x in range(prev[-1] + step, a, step)]
                gap.discard(series)
            out.append((a, "g" if st == "f" else st))
            last_a = a
            continue
        m = re.fullmatch(r"(m\d?|g|ls|hs)", it)            # '68g,m' -> another state of the last A
        if m and last_a is not None:
            out.append((last_a, m[1]))
            continue
        return None
    return out


def observables(text: str) -> dict[str, int]:
    t = text.replace(" ", "")
    return {"I": int(bool(re.search(r"(^|,)I(,|$)", t))), "mu": int("μ" in t or "mu" in t),
            "Q": int("Q" in t), "dr2": int("r2" in t or "r 2" in text or "ΔνIS" in t)}


def main() -> None:
    req = urllib.request.Request(URL, headers={"User-Agent": "nuclear-chart-plotter (github.com/jonas-ka)"})
    html = urllib.request.urlopen(req).read().decode("utf-8", errors="replace")
    today = dt.date.today().isoformat()
    records, unparsed, element, z = [], [], None, None
    for cells in rows(html):
        if len(cells) == 7:
            element, z, a_spec, data, tech, fac, ref = cells
        else:                          # a continuation row of the last element
            a_spec, data, tech, fac, ref = cells[-5:]
        el = element.split()[0] if element else ""
        try:
            zi = int(re.sub(r"\D", "", z))
        except ValueError:
            unparsed.append(f"Z?\t{z}\t{a_spec}\t{ref}")
            continue
        if not re.fullmatch(r"[A-Z][a-z]?", el):           # molecules (RaF, AcF) and ions (Pb81+)
            unparsed.append(f"{el}\t{zi}\t{a_spec}\t{data}\t{ref}\t(not an atom: skipped)")
            continue
        nuclides = expand(a_spec)
        if nuclides is None:
            unparsed.append(f"{el}\t{zi}\t{a_spec}\t{data}\t{ref}")
            continue
        obs = observables(data)
        for a, state in nuclides:
            records.append({"Z": zi, "A": a, "N": a - zi, "state": state, "element": el, **obs, "data": data,
                            "technique": tech, "facility": fac, "reference": ref, "read": today})
    df = pd.DataFrame(records)
    df.to_csv(OUT, index=False)
    UNPARSED.write_text(f"# entries not expanded automatically, read {today} from\n# {URL}\n" + "\n".join(unparsed) + "\n")
    nuclides = df[["Z", "N"]].drop_duplicates()
    print(f"{len(df)} rows, {len(nuclides)} nuclides (ground state or isomer), {df.Z.nunique()} elements; "
          f"{len(unparsed)} entries for a manual check -> {OUT.name}")


if __name__ == "__main__":
    main()
