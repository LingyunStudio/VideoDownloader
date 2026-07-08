; VideoDownloader Inno Setup script
; Compiled by build.ps1 via ISCC.exe -> dist\VideoDownloader_Setup.exe
; Standalone:  ISCC.exe installer.iss

#define MyAppName        "VideoDownloader"
#define MyAppVersion     "2.1"
#define MyAppPublisher   "VideoDownloader"
#define MyAppExeName     "VideoDownloader.exe"
#define MyAppIcon        "icon\1.ico"

[Setup]
AppId={{8F3C2A1E-5B6D-4E7A-9C0B-VIDEODL2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=VideoDownloader_Setup
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
Uninstallable=yes
; 自更新静默安装时关闭占用进程的旧版；UsePreviousAppDir=yes(默认)使装回原目录
CloseApplications=force

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; entire onedir output (incl. yt-dlp-bundled) into install dir
Source: "dist\VideoDownloader\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
; 仅静默自更新后重启新版：正常安装不自动打开（skipifnotsilent）；/VERYSILENT 下执行
Filename: "{app}\{#MyAppExeName}"; Flags: nowait skipifnotsilent

[UninstallDelete]
; clean program dir residue; user data in %APPDATA% is left untouched
Type: filesandordirs; Name: "{app}\_internal"
Type: dirifempty;    Name: "{app}"
