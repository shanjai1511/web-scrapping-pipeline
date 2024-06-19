$excludedFolders = @("__pycache__", "myenv")
$rootPath = "."

# Function to recursively get the directory structure
function Get-Tree {
    param (
        [string]$path,
        [string]$indent = ""
    )

    # Get all items in the directory excluding the specified folders
    $items = Get-ChildItem -Path $path -Force | Where-Object {
        $excludedFolders -notcontains $_.Name
    }

    foreach ($item in $items) {
        Write-Output "$indent$item"
        if ($item.PSIsContainer) {
            Get-Tree -path $item.FullName -indent "$indent    "
        }
    }
}

# Start the process and write to tree.txt
Get-Tree -path $rootPath | Out-File -FilePath tree.txt
