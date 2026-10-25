#define AppName "SparkTwin"
#define AppVersion "0.1.0"
#define Publisher "Md Najmul Hossain"

[Setup]
AppId={{E0C086A4-9704-4627-99BC-B219859B4A01}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion} Developer Preview
AppPublisher={#Publisher}
AppPublisherURL=https://github.com/hossain0707/SparkTwin
AppSupportURL=https://github.com/hossain0707/SparkTwin/issues
AppUpdatesURL=https://github.com/hossain0707/SparkTwin/releases
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
OutputDir=dist\release
OutputBaseFilename=SparkTwin-Setup-Windows-x64
UninstallDisplayIcon={app}\SparkTwin.exe

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "dist\SparkTwin\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\SparkTwin"; Filename: "{app}\SparkTwin.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\SparkTwin"; Filename: "{app}\SparkTwin.exe"; Tasks: desktopicon; WorkingDir: "{app}"

[Run]
Filename: "{app}\SparkTwin.exe"; Description: "Launch SparkTwin"; Flags: nowait postinstall skipifsilent
