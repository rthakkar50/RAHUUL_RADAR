[Setup]
AppName=RAHUUL RADAR PRO
AppVersion=1.0
DefaultDirName={pf}\RAHUUL_RADAR
DefaultGroupName=RAHUUL RADAR PRO
OutputDir=Output
OutputBaseFilename=RAHUUL_RADAR_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=dist\RAHUUL_RADAR_PRO\_internal\ui\assets\logo.ico

[Files]
Source: "dist\RAHUUL_RADAR_PRO\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\RAHUUL RADAR PRO"; Filename: "{app}\RAHUUL_RADAR_PRO.exe"
Name: "{commondesktop}\RAHUUL RADAR PRO"; Filename: "{app}\RAHUUL_RADAR_PRO.exe"

[Run]
Filename: "{app}\RAHUUL_RADAR_PRO.exe"; Description: "Launch RAHUUL RADAR PRO"; Flags: nowait postinstall skipifsilent
