"""Download + crack the 6-member ICOS PARIS C2F6 (pfc218) posterior ensemble (Europe, FLAT prior).
Same collection + mechanism as the CF4 leg (DOI 10.18160/GR1Q-6SK4, n8myDc-I-gbHkdt3ajIYLLDe).
This is the PFC artifact's C2F6 leg. Run:  python src/fetch_posteriors.py
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

# 6 C2F6 (pfc218) members of the ICOS PARIS F-gas collection (full object hashes).
MEMBERS = {
    "ELRIS_FLEXPART": "dmzGyBBWE3cfDNZfIYSxeTDKMPXKJCkPq0u2D5n5Rfw",
    "ELRIS_NAME": "Z2efOYC8smA9E0xGx9V_flICZQhVhxRZxZSJm5mhF98",
    "InTEM_FLEXPART": "jW-AmVdmhS9VaErcaEcXppUF4iC71wFUyCrGdaC_g7w",
    "InTEM_NAME": "TphsD1CLxf2m7ZBtcBJswSAYpUG-ZEmkOUcP9SHwa4U",
    "RHIME_FLEXPART": "sUUYKLp6W7fqyb316xWn9a44fvbhAlbhb0fOhI6GASM",
    "RHIME_NAME": "iGRF-t7ZRpU482IjTE-nDLwgWtqCgljBwlR4CLX1a5g",
}
OBJ_URL = "https://data.icos-cp.eu/objects/{h}"


def fetch_one(label, h):
    os.makedirs(ICOS, exist_ok=True)
    zip_fp = os.path.join(ICOS, f"_{label}_pfc218.zip")
    if not os.path.exists(zip_fp):
        req = urllib.request.Request(OBJ_URL.format(h=h),
                                     headers={"User-Agent": UA, "Cookie": f"CpLicenseAcceptedFor={h}"})
        with urllib.request.urlopen(req, timeout=300) as r, open(zip_fp, "wb") as f:
            f.write(r.read())
    with zipfile.ZipFile(zip_fp) as z:
        flux = [n for n in z.namelist() if n.endswith("_yearly_flux.nc")]
        assert len(flux) == 1, f"{label}: expected 1 flux file, got {flux}"
        return z.extract(flux[0], ICOS)


def main():
    print(f"[icos] fetching {len(MEMBERS)} C2F6 (pfc218) posterior members -> {ICOS}")
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
    print("\n[VERDICT] 6-member C2F6 Europe posterior ensemble obtained + cracked." if has_post
          else "\n[WARN] flux_total_posterior NOT found.")


if __name__ == "__main__":
    main()
