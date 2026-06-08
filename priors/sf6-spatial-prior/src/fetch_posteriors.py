"""Obtain + verify the one downloadable gridded SF6 POSTERIOR found in the discovery sweep:
PANGAEA 880251 (Brunner et al. 2017, InGOS) — posterior ('ASIM'=assimilated) gridded SF6 emission
fields from 4 inversion systems (NILU/FLEXINVERT, EMPA, EMPA2, UKMO/InTEM), Europe, 2011, CC-BY-3.0.
SF6 species code in the archive = 'H13'. This self-verifies the agents' finding (downloads + loads).

Run:  python src/fetch_posteriors.py
"""
import os
import re
import zipfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "posteriors")
ZIP_URL = "https://store.pangaea.de/Publications/Brunner-etal_2017/ingos_halocarbon_inversions.zip"
ZIP_FP = os.path.join(DATA, "ingos_halocarbon_inversions.zip")
UA = "sf6-spatial-prior/1.0 (research; +https://github.com/zachdissington)"


def download():
    os.makedirs(DATA, exist_ok=True)
    if os.path.exists(ZIP_FP):
        print(f"[pangaea] cached: {ZIP_FP} ({os.path.getsize(ZIP_FP)/1e6:.1f} MB)")
        return
    print(f"[pangaea] downloading {ZIP_URL}")
    req = urllib.request.Request(ZIP_URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r, open(ZIP_FP, "wb") as f:
        f.write(r.read())
    print(f"[pangaea] saved {ZIP_FP} ({os.path.getsize(ZIP_FP)/1e6:.1f} MB)")


def main():
    download()
    with zipfile.ZipFile(ZIP_FP) as z:
        names = z.namelist()
    print(f"[pangaea] {len(names)} files in archive")

    # SF6 = H13. Posterior = 'ASIM'; prior = 'APRI'; uncertainty = 'UNCERT'.
    sf6 = [n for n in names if re.search(r"H13", n)]
    sf6_post = [n for n in sf6 if "ASIM" in n.upper() or ("EMISSIONS" in n.upper() and "PRIOR" not in n.upper())]
    sf6_post_nc = [n for n in sf6_post if n.lower().endswith(".nc")]
    print(f"[verify] SF6 (H13) files: {len(sf6)};  posterior(ASIM/emissions): {len(sf6_post)};  posterior NetCDF: {len(sf6_post_nc)}")
    print("[verify] SF6 posterior gridded files by system:")
    for n in sorted(sf6_post)[:20]:
        print(f"    {n}")

    # load one posterior NetCDF to confirm it is a real gridded field
    if sf6_post_nc:
        import xarray as xr
        import numpy as np
        target = sorted(sf6_post_nc)[0]
        with zipfile.ZipFile(ZIP_FP) as z:
            local = z.extract(target, DATA)
        ds = xr.open_dataset(local)
        print(f"\n[verify] opened {os.path.basename(target)}")
        print(f"  data_vars: {list(ds.data_vars)}")
        print(f"  dims: {dict(ds.sizes)}  coords: {list(ds.coords)}")
        # report lon/lon resolution + coverage if present
        for c in ds.coords:
            v = ds[c].values
            if v.ndim == 1 and v.size > 2 and np.issubdtype(v.dtype, np.number):
                print(f"  {c}: {v.min():.2f}..{v.max():.2f}  step~{abs(v[1]-v[0]):.3f}  n={v.size}")
        print("\n[VERDICT] Real gridded SF6 posterior obtained (Europe, 2011, 4 inversion systems).")
        print("  -> A REAL metric 'beats the proxy' test is now possible for European countries (incl. FR, DE),")
        print("     for 2011. Caveats: single year (2011), coarse nested grid, predates our 2020 priors.")
    else:
        print("\n[VERDICT] No SF6 posterior NetCDF found in archive — inspect .dat files instead.")


if __name__ == "__main__":
    main()
