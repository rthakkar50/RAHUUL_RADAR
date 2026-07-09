# INSTALL GUIDE

## 1. Download
Download the latest `RAHUUL_RADAR_v1.0_Setup.exe` from the official distribution portal. Alternatively, download the portable `.zip` version.

## 2. Install
1. Double-click the installer (`RAHUUL_RADAR_v1.0_Setup.exe`).
2. Follow the on-screen prompts to select your installation directory.
3. Check the box to "Create Desktop Shortcut".
4. Click **Install**.

## 3. First Launch
Upon launching the application for the first time:
- The system will automatically build localized directories (`/logs`, `/exports`, `/config`, `/cache`).
- A default configuration profile will be applied.
- The UI will prompt you if any required system fonts are missing.

## 4. Common Problems
- **Visual C++ Redistributable Error**: If you receive a `.dll` missing error on launch, download and install the latest Microsoft Visual C++ Redistributable (2015-2022).
- **Missing Write Permissions**: Ensure the application is NOT installed in a restricted directory where it cannot write to its `/logs` folder, or run the application as Administrator.

## 5. Windows Defender / Antivirus
Because this is newly compiled software, Windows Defender or third-party Antivirus (Avast, Norton) may flag the executable as "Unrecognized" (SmartScreen).
- **Fix**: Click **More Info** -> **Run Anyway**.
- Add the installation folder to your Antivirus exception list to prevent the scanner cache from being quarantined.

## 6. Updates
Updates will be distributed as patch installers. To update, simply run the new installer over the existing directory to overwrite core engine files while preserving your `/config` and `/logs`.
