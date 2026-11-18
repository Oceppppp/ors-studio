#define MyAppName "Operations Research Studio"
#define MyAppVersion "0.4.0"
#define MyAppPublisher "ORS Studio Contributors"
#define MyAppExeName "ORS-Studio.exe"

[Setup]
AppId={{B4E2D6A3-C9D1-4D3B-A97E-0200AABBCCDD}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\ORS Studio
DefaultGroupName={#MyAppName}
OutputDir=..
OutputBaseFilename=ORS-Studio-Setup-0.4.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupLogging=yes

[Files]
Source: "..\dist\ORS-Studio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Operations Research Studio"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Operations Research Studio"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Operations Research Studio"; Flags: nowait postinstall skipifsilent
