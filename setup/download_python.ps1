# Self-elevate the script if required
if (-Not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) {
 if ([int](Get-CimInstance -Class Win32_OperatingSystem | Select-Object -ExpandProperty BuildNumber) -ge 6000) {
  $CommandLine = "-File `"" + $MyInvocation.MyCommand.Path + "`" " + $MyInvocation.UnboundArguments
  Start-Process -FilePath PowerShell.exe -Verb Runas -ArgumentList $CommandLine
  Exit
 }
}


# Python install variables
$pythonVersion = "3.10.4"
$pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion.exe"
$pythonDownloadPath = "C:\Program Files (x86)\Python\python-$pythonVersion-installer.exe"
$pythonInstallDir = "C:\Program Files (x86)\Python\Python$pythonVersion"

# Create the Python/ directory if needed
if (Test-Path -Path 'C:\Program Files (x86)\Python') {
    # Path exists
} else {
    # Create Python dir
    New-Item -Path 'C:\Program Files (x86)\Python' -ItemType Directory
}

# Run installer
(New-Object Net.WebClient).DownloadFile($pythonUrl, $pythonDownloadPath)
& $pythonDownloadPath InstallAllUsers=1 PrependPath=0 Include_test=0 TargetDir=$pythonInstallDir
# Append to PATH environment variable
[Environment]::SetEnvironmentVariable("PATH", $Env:PATH + ";" + $pythonInstallDir, [EnvironmentVariableTarget]::Machine)

exit $LASTEXITCODE