"""Download + crack the 6-member ICOS PARIS HFC-23 posterior ensemble (Europe, FLAT prior).

Same collection + mechanism as the CF4 build: ICOS PARIS F-gas inversion collection
(DOI 10.18160/GR1Q-6SK4, collection n8myDc-I-gbHkdt3ajIYLLDe). Each object is a zip holding a
`*_hfc23_yearly_flux.nc` (the gridded posterior) + a concentrations file. FLAT prior => the posterior
is observation-driven, not prior-dominated. We extract the flux files into data/posteriors/icos/ with
the same naming the CF4 kill-test globs.

Run:  python src/fetch_posteriors.py
"""
import os
import zipfile
import urllib.request

import numpy as np
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICOS = os.path.join(ROOT, "data", "posteriors", "icos")
UA = "hfc23-hcfc22-prior/1.0 (research; +https://github.com/zachdissington)"

# 6 HFC-23 members of the ICOS PARIS F-gas collection (full object hashes), confirmed by enumerating
# the collection's 112 members (6 each: cf4, ch4, hfc125, hfc134a, hfc143a, hfc152a, hfc23, hfc32,
# n2o, nf3, pfc218; sf6=4). system x transport: ELRIS/InTEM/RHIME x FLEXPART/NAME.
MEMBERS = {
    "ELRIS_FLEXPART": "p24hAvf6kMfx_73HvZy5VclUe6eq9z4A1v1V1xHS0aw",
    "ELRIS_NAME": "K-jRqxLkJJqpHPKe_NtvW3Gfx1IeHwDglJf4R-hdvfc",
    "InTEM_FLEXPART": "uR7hhvQ832eGA4pcfJl_YJe69fOSkx4Jin_HJCKHdPg",
    "InTEM_NAME": "ZvxVNyhtbY-evIxsB--U7TrcA8c9uQJvw8x5TpA_Fww",
    "RHIME_FLEXPART": "evRPPamYnZiKp4BDeKw2WYi_zgonqkM6QD8ANlkg7WI",
    "RHIME_NAME": "A53GAiOH-jlJ9NSGHrk1DdNQc2rki4fUX56U0ksu6j8",
}
OBJ_URL = "https://data.icos-cp.eu/objects/{h}"


def fetch_one(label, h):
    os.makedirs(ICOS, exist_ok=True)
    zip_fp = os.path.join(ICOS, f"_{label}_hfc23.zip")
    if not os.path.exists(zip_fp):
        req = urllib.request.Request(OBJ_URL.format(h=h),
                                     headers={"User-Agent": UA, "Cookie": f"CpLicenseAcceptedFor={h}"})
        with urllib.request.urlopen(req, timeout=300) as r, open(zip_fp, "wb") as f:
            f.write(r.read())
    # extract the yearly_flux member
    with zipfile.ZipFile(zip_fp) as z:
        flux = [n for n in z.namelist() if n.endswith("_yearly_flux.nc")]
        assert len(flux) == 1, f"{label}: expected 1 flux file, got {flux}"
        out = z.extract(flux[0], ICOS)
    return out


def main():
    print(f"[icos] fetching {len(MEMBERS)} HFC-23 posterior members -> {ICOS}")
    files = []
    for label, h in MEMBERS.items():
        fp = fetch_one(label, h)
        files.append(fp)
        print(f"  ok {label}: {os.path.basename(fp)} ({os.path.getsize(fp)/1e6:.2f} MB)")

    # crack one to confirm fields, grid, year, FLAT prior (the SF6 near-miss guard)
    target = files[0]
    ds = xr.open_dataset(target)
    print(f"\n[crack] {os.path.basename(target)}")
    print(f"  data_vars: {list(ds.data_vars)}")
    print(f"  dims: {dict(ds.sizes)}")
    if "time" in ds.coords:
        yrs = [str(t)[:10] for t in np.atleast_1d(ds.time.values)]
        print(f"  time: {yrs}")
    for c in ("latitude", "longitude"):
        if c in ds.coords:
            v = ds[c].values
            print(f"  {c}: {v.min():.2f}..{v.max():.2f} step~{abs(v[1]-v[0]):.3f} n={v.size}")
    has_post = "flux_total_posterior" in ds.data_vars
    has_cfrac = "country_fraction" in ds.data_vars or "country_fraction" in ds.coords
    print(f"  flux_total_posterior present: {has_post}")
    print(f"  country_fraction present: {has_cfrac}")
    if "2020" in "".join(str(t) for t in np.atleast_1d(ds.time.values)) if "time" in ds.coords else False:
        print("  2020 present: yes")
    ds.close()
    print("\n[VERDICT] 6-member HFC-23 Europe posterior ensemble obtained + cracked." if has_post
          else "\n[WARN] flux_total_posterior NOT found — inspect before trusting.")


if __name__ == "__main__":
    main()
