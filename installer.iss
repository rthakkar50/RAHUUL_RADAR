[Setup]
AppName=RAHUUL RADAR PRO
AppVersion=1.0.0
AppPublisher=Rahul Thakkar
DefaultDirName={pf}\RAHUUL RADAR PRO
DefaultGroupName=RAHUUL RADAR PRO
OutputDir=Output
OutputBaseFilename=RAHUUL_RADAR_v1.0_Setup
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile=resources\app_icon.ico
UninstallDisplayIcon={app}\RahuulRadarPro.exe

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\RahuulRadarPro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "logs\*"; DestDir: "{app}\logs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "exports\*"; DestDir: "{app}\exports"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "fonts\*"; DestDir: "{app}\fonts"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\RAHUUL RADAR PRO"; Filename: "{app}\RahuulRadarPro.exe"
Name: "{group}\Uninstall RAHUUL RADAR PRO"; Filename: "{uninstallexe}"
Name: "{commondesktop}\RAHUUL RADAR PRO"; Filename: "{app}\RahuulRadarPro.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\RahuulRadarPro.exe"; Description: "Launch RAHUUL RADAR PRO"; Flags: nowait postinstall skipifsilent

[Dirs]
Name: "{app}\logs"
Name: "{app}\exports"
Name: "{app}\config"
Name: "{app}\cache"
Name: "{app}\reports"
Name: "{app}\backups"
