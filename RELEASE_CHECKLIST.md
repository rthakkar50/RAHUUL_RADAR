# RAHUUL RADAR Pro - Release Checklist

Follow this checklist strictly before creating a final distribution to ensure zero-leakage of developer secrets, local database states, or unneeded cache files.

## 1. Clean Environment Verification
- [ ] Ensure `.gitignore` is up to date (should exclude `.env`, `config.json`, `scratch/`, `logs/`, `.db` files, and `.DS_Store`).
- [ ] Run `git clean -n -d -x` (dry run) to preview unversioned cache files that would be removed. Be careful not to delete files you need.
- [ ] Delete `build/` and `dist/` directories completely before a fresh build.

## 2. Dependency Audit
- [ ] Ensure `.venv` has all recent `requirements.txt` installed (`pip install -r requirements.txt`).
- [ ] Run test suite locally (`python -m pytest tests/ -v`) to confirm 100% test pass rate.

## 3. Local State Cleansing
The application automatically creates `config.json` and database schemas at runtime if missing. Ensure your developer local states are **NOT** bundled:
- [ ] Confirm `data/radar.db`, `data/paper_trading.db`, and `data/trade_journal.db` are **NOT** referenced in the PyInstaller `datas` tuple.
- [ ] Confirm `config.json` is **NOT** referenced in the `datas` tuple in the PyInstaller spec.
- [ ] Check `logs/` directory is not packaged.

## 4. Build Process
Use the unified canonical specification file (`RAHUUL_RADAR.spec`) to build:
```bash
# Activate virtual environment
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

# Clean build
pyinstaller --clean RAHUUL_RADAR.spec
```

## 5. Post-Build Verification
Before zipping or deploying the `.app` / `.exe`:
- [ ] Open the output `dist/` folder.
- [ ] Navigate into the `dist/RAHUUL_RADAR/` bundle (or Show Package Contents on Mac).
- [ ] Check for `.env` or `config.json` - if they exist in the app bundle, **the build has leaked secrets**. Abort and fix the `.spec`.
- [ ] Launch the executable manually on the build machine. It should start gracefully, spawn a fresh empty database, and prompt for initial configuration.
- [ ] Check that `ui/assets/` (like icons) loaded properly in the built executable.

## 6. Distribution Packaging
- [ ] Mac: Create a DMG file containing `RAHUUL RADAR.app`.
- [ ] Windows: Compile an installer (e.g., using Inno Setup or NSIS) or create a self-extracting zip of the `dist/RAHUUL_RADAR/` folder.
