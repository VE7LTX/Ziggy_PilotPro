<#
-------------------------------------------------------------------------------
                     DLLs Copying Script for Windows
-------------------------------------------------------------------------------

Description:
    This script automates the process of searching for specific DLLs within the Windows directories.
    Once found, it copies these DLLs to a designated build folder.

Purpose:
    To assist in setting up and deploying applications by ensuring necessary DLLs are present in the build directory.

Usage:
    Execute the script using PowerShell. Ensure you have the necessary permissions to search and copy files on your system.

Note:
    Before executing, make sure the destination directory exists and the script is run with appropriate permissions.

Author:
    Matthew Schafer
    Date: August 31, 2023

-------------------------------------------------------------------------------
#>

# Define the list of DLLs that need to be copied.
# These DLLs are essential for the functioning of certain applications and may not be present in all environments.
$dlls = @("vcomp140.dll", "msvcp140.dll")

# Start looping through each DLL in the list.
# The goal is to locate each DLL in the Windows directories and copy it to the build folder.
foreach ($dll in $dlls) {
    # Using Get-ChildItem to search for the DLL in both System32 and SysWOW64 directories.
    # The `-Filter` parameter helps in narrowing down the search to files that match the DLL name.
    # `-Recurse` ensures that all subdirectories are also searched.
    # `-ErrorAction SilentlyContinue` ensures that the script doesn't halt if an error occurs during the search.
    # `Select-Object -First 1` ensures that we get only the first match if there are multiple copies of the DLL.
    $file = Get-ChildItem -Path C:\Windows\System32\, C:\Windows\SysWOW64\ -Filter $dll -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    
    # Check if the DLL was found.
    if ($file) {
        # If found, copy the DLL to the specified build directory.
        # Ensure the destination directory exists before copying.
        Copy-Item -Path $file.FullName -Destination "C:\VS Code Workspaces\Ziggy_PilotPro\build\exe.win-amd64-3.11\"
        
        # Notify the user that the DLL was copied successfully.
        Write-Output "$dll copied successfully!"
    } else {
        # Notify the user if the DLL was not found.
        Write-Output "$dll not found!"
    }
}

<#
-------------------------------------------------------------------------------
End of Script.
Ensure you verify the copying process and make sure all necessary DLLs are present in the target directory.
For any issues, refer to the script logs or contact the script author.
-------------------------------------------------------------------------------
#>
