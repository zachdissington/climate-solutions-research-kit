"""Download + crack the 6-member ICOS PARIS CF4 posterior ensemble (Europe, FLAT prior).

This is the CF4 leg of the PFC artifact — the GROUND-TRUTH posterior that cf4_killtest.py,
holistic_significance.py and enrichment_v2.py read (they glob `data/posteriors/icos/*cf4_yearly_flux.nc`).
fetch_posteriors.py only pulls the C2F6 (pfc218) members of the same collection, so a clean clone has
no way to obtain the CF4 ensemble without this script.

Source: ICOS PARIS F-gas inversion collection, DOI 10.18160/GR1Q-6SK4
(collection URI meta.icos-cp.eu/collections/n8myDc-I-gbHkdt3ajIYLLDe), CC-BY-4.0. 6 CF4 members:
ELRIS/InTEM/RHIME x FLEXPART/NAME, Europe domain 391x293, yearly (incl. 2020), FLAT prior
(observation-driven). The six object IDs below are the CF4 members listed in factors/SOURCES.md
("CF4 inversion posterior" section) — keep them in sync with that file.

Mechanism mirrors fetch_posteriors.py exactly: ICOS cookie download
(`curl -L -b "CpLicenseAcceptedFor=<id>" .../objects/<id>`), then unzip the `*cf4_yearly_flux.nc`.

NOTE: the downloaded `.nc` files (and the `_*_cf4.zip` archives) are large and gitignored
(see .gitignore: data/, *.nc). They are cached locally; this script REGENERATES them from ICOS for a
clean clone. The downstream scripts already find the cached copies, so a download is only needed on a
fresh checkout. Run:  python src/fetch_cf4_posteriors.py
"""
import os
import zipfile
import urllib.request

import numpy as np
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICOS = os.path.join(ROOT, "data", "posteriors", "icos")
UA = "pfc-aluminium-prior/1.0 (research; +https://github.com/zachdissington)"

# 6 CF4 members of the ICOS PARIS F-gas collection (object IDs, must match factors/SOURCES.md).
MEMBERS = {
    "ELRIS_FLEXPART": "Y6dWqMGLwjtsU-Hup-HPJSIX",
    "ELRIS_NAME": "CTLyibdOgwZx7MFmv5DhJyoD",
    "InTEM_FLEXPART": "YjZ3lH2o_GSZqUI0uG1r3UoL",
    "InTEM_NAME": "YvaN2detryM0WUM35R3dLT4M",
    "RHIME_FLEXPART": "GB9UGW2D4Erm7IxxElpkamkX",
    "RHIME_NAME": "3jC--jBn_uzddEF-k7SQI1bR",
}
OBJ_URL = "https://data.icos-cp.eu/objects/{h}"


def fetch_one(label, h):
    os.makedirs(ICOS, exist_ok=True)
    zip_fp = os.path.join(ICOS, f"_{label}_cf4.zip")
    if not os.path.exists(zip_fp):
        req = urllib.request.Request(OBJ_URL.format(h=h),
                                     headers={"User-Agent": UA, "Cookie": f"CpLicenseAcceptedFor={h}"})
        with urllib.request.urlopen(req, timeout=300) as r, open(zip_fp, "wb") as f:
            f.write(r.read())
    with zipfile.ZipFile(zip_fp) as z:
        flux = [n for n in z.namelist() if n.endswith("cf4_yearly_flux.nc")]
        assert len(flux) == 1, f"{label}: expected 1 CF4 flux file, got {flux}"
        return z.extract(flux[0], ICOS)


def main():
    print(f"[icos] fetching {len(MEMBERS)} CF4 posterior members -> {ICOS}")
    files = []
    for label, h in MEMBERS.items():
        fp = fetch_one(label, h)
        files.append(fp)
        print(f"  ok {label}: {os.path.basename(fp)} ({os.path.getsize(fp)/1e6:.2f} MB)")
    ds = xr.open_dataset(files[0])
    print(f"\n[crack] {os.path.basename(files[0])}")
    print(f"  dims: {dict(ds.sizes)}")
    if "time" in ds.coords:
        print(f"  time: {[str(t)[:10] for t in np.atleast_1d(ds.time.values)]}")
    has_post = "flux_total_posterior" in ds.data_vars
    print(f"  flux_total_posterior: {has_post}; country_fraction: {'country_fraction' in ds.data_vars}")
    ds.close()
    print("\n[VERDICT] 6-member CF4 Europe posterior ensemble obtained + cracked." if has_post
          else "\n[WARN] flux_total_posterior NOT found.")


if __name__ == "__main__":
    main()
