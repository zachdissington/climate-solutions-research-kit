"""Download + crack the 6-member ICOS PARIS NF3 posterior ensemble (Europe, FLAT prior).
Same collection + mechanism as the CF4/HFC-23 builds (DOI 10.18160/GR1Q-6SK4).
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
UA = "nf3-fabs-prior/1.0 (research; +https://github.com/zachdissington)"

# 6 NF3 members of the ICOS PARIS F-gas collection (full object hashes).
MEMBERS = {
    "ELRIS_FLEXPART": "P3dcgAtQ71_oFj8rj2MDrI5wo4U0IvFQqdiJaR9WBXw",
    "ELRIS_NAME": "Dl-kCYsfoz9B56UBoXDQ_yPtLPeUtYrETuXUj5ATJxE",
    "InTEM_FLEXPART": "mpx5-FuEOkiiesrw4s2eM4G3qPugSi9naDDFip0RbCM",
    "InTEM_NAME": "uKTqXJ2kdVQR1rYcUu1EbVeSVL039b2E6wgERtZIqb8",
    "RHIME_FLEXPART": "p9Vn1XMaBZo4o3t0fCKAUTj3cgl_6VIAxTRExP7ej1A",
    "RHIME_NAME": "OXLtFCQDV7xbzeQzNwxdBNwK7wEVdpunAORwaoJhl8I",
}
OBJ_URL = "https://data.icos-cp.eu/objects/{h}"


def fetch_one(label, h):
    os.makedirs(ICOS, exist_ok=True)
    zip_fp = os.path.join(ICOS, f"_{label}_nf3.zip")
    if not os.path.exists(zip_fp):
        req = urllib.request.Request(OBJ_URL.format(h=h),
                                     headers={"User-Agent": UA, "Cookie": f"CpLicenseAcceptedFor={h}"})
        with urllib.request.urlopen(req, timeout=300) as r, open(zip_fp, "wb") as f:
            f.write(r.read())
    with zipfile.ZipFile(zip_fp) as z:
        flux = [n for n in z.namelist() if n.endswith("_yearly_flux.nc")]
        assert len(flux) == 1, f"{label}: expected 1 flux file, got {flux}"
        out = z.extract(flux[0], ICOS)
    return out


def main():
    print(f"[icos] fetching {len(MEMBERS)} NF3 posterior members -> {ICOS}")
    files = []
    for label, h in MEMBERS.items():
        fp = fetch_one(label, h)
        files.append(fp)
        print(f"  ok {label}: {os.path.basename(fp)} ({os.path.getsize(fp)/1e6:.2f} MB)")
    ds = xr.open_dataset(files[0])
    print(f"\n[crack] {os.path.basename(files[0])}")
    print(f"  data_vars: {[v for v in ds.data_vars][:6]}...")
    print(f"  dims: {dict(ds.sizes)}")
    if "time" in ds.coords:
        print(f"  time: {[str(t)[:10] for t in np.atleast_1d(ds.time.values)]}")
    has_post = "flux_total_posterior" in ds.data_vars
    print(f"  flux_total_posterior present: {has_post}; country_fraction present: {'country_fraction' in ds.data_vars}")
    ds.close()
    print("\n[VERDICT] 6-member NF3 Europe posterior ensemble obtained + cracked." if has_post
          else "\n[WARN] flux_total_posterior NOT found.")


if __name__ == "__main__":
    main()
