"""Download + crack the 6-member ICOS PARIS HFC-134a posterior ensemble (Europe).

Same collection + mechanism as the CF4/HFC-23 builds: ICOS PARIS F-gas inversion collection
(DOI 10.18160/GR1Q-6SK4, collection n8myDc-I-gbHkdt3ajIYLLDe). Each object is a zip holding a
`*_yearly_flux.nc` (the gridded posterior) + a concentrations file. Hashes below were obtained by
enumerating the collection's 112 members via the ICOS metadata API and filtering name~'hfc134a'.

CAVEAT (unlike HFC-23's FLAT prior): the HFC-134a inversion (ACP 26-7647-2026) uses an
EDGAR/population-weighted prior, so the posterior is partly biased toward population. This makes the
kill-test CONSERVATIVE — a cooling-demand prior that still beats population here is a strong signal.

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
UA = "hfc134a-refrigerant-bank-prior/1.0 (research; +https://github.com/zachdissington)"

# 6 HFC-134a members of the ICOS PARIS F-gas collection (full 43-char object hashes), confirmed by
# enumerating the collection's 112 members (meta.icos-cp.eu/collections/n8myDc-I-gbHkdt3ajIYLLDe)
# and filtering name~'hfc134a'. system x transport: ELRIS/InTEM/RHIME x FLEXPART/NAME.
MEMBERS = {
    "ELRIS_FLEXPART": "tTxCm5xDOUgu_Bvn4uqzJLFNsN2vDI1YEHBTAWSZcG0",
    "ELRIS_NAME": "qF_x3ZSDmjU7_2HDPROEtOXHd4huFSFLARX1mxqrjRk",
    "InTEM_FLEXPART": "nrqp06Ham0bph3M7-NlZMGite_Q9KWgp9urbSkRGtbs",
    "InTEM_NAME": "vDcGDMekgTrzzjKE6LhZ5X3QX4BnWX68hjJU8VBNjpc",
    "RHIME_FLEXPART": "pRJynfjXlC79MGLCg9C814HvFDeJcSH6BrdaF5Ojm-4",
    "RHIME_NAME": "TU5T1sa4wuzv-CbJclui8dsP0ws_gyBAXVyNqH8bBX4",
}
OBJ_URL = "https://data.icos-cp.eu/objects/{h}"


def fetch_one(label, h):
    os.makedirs(ICOS, exist_ok=True)
    zip_fp = os.path.join(ICOS, f"_{label}_hfc134a.zip")
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
    print(f"[icos] fetching {len(MEMBERS)} HFC-134a posterior members -> {ICOS}")
    files = []
    for label, h in MEMBERS.items():
        fp = fetch_one(label, h)
        files.append(fp)
        print(f"  ok {label}: {os.path.basename(fp)} ({os.path.getsize(fp)/1e6:.2f} MB)")

    # crack one to confirm fields, grid, year (the SF6 near-miss guard)
    target = files[0]
    ds = xr.open_dataset(target)
    print(f"\n[crack] {os.path.basename(target)}")
    print(f"  data_vars: {list(ds.data_vars)}")
    print(f"  dims: {dict(ds.sizes)}")
    yrs = []
    if "time" in ds.coords:
        yrs = [str(t)[:10] for t in np.atleast_1d(ds.time.values)]
        print(f"  time: {yrs}")
    for c in ("latitude", "longitude"):
        if c in ds.coords:
            v = ds[c].values
            print(f"  {c}: {v.min():.3f}..{v.max():.3f} step~{abs(v[1]-v[0]):.4f} n={v.size}")
    has_post = "flux_total_posterior" in ds.data_vars
    has_cfrac = "country_fraction" in ds.data_vars or "country_fraction" in ds.coords
    has_2020 = any(y.startswith("2020") for y in yrs)
    print(f"  flux_total_posterior present: {has_post}")
    print(f"  country_fraction present: {has_cfrac}")
    print(f"  2020 present: {has_2020}")
    ds.close()
    print("\n[VERDICT] 6-member HFC-134a Europe posterior ensemble obtained + cracked." if has_post
          else "\n[WARN] flux_total_posterior NOT found — inspect before trusting.")


if __name__ == "__main__":
    main()
