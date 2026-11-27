param(
    [Parameter(Mandatory=$true)][string[]]$Document,
    [string]$PreviewDirectory,
    [string]$OpenXmlAssembly
)
$ErrorActionPreference = 'Stop'
$paths = @($Document | ForEach-Object { (Resolve-Path -LiteralPath $_).ProviderPath })
if ($PreviewDirectory) {
    $PreviewDirectory = (Resolve-Path -LiteralPath $PreviewDirectory).ProviderPath
}
if ($OpenXmlAssembly) {
    Add-Type -AssemblyName WindowsBase
    $assembly = [Reflection.Assembly]::LoadFrom((Resolve-Path -LiteralPath $OpenXmlAssembly).ProviderPath)
    $validator = [DocumentFormat.OpenXml.Validation.OpenXmlValidator]::new()
    foreach ($path in $paths) {
        $package = [DocumentFormat.OpenXml.Packaging.WordprocessingDocument]::Open($path, $false)
        try {
            $issues = @($validator.Validate($package))
            [pscustomobject]@{ File = [IO.Path]::GetFileName($path); SDK = $assembly.GetName().Version.ToString(); Errors = $issues.Count }
            if ($issues.Count) {
                $issues | Select-Object -First 12 Description, Path
                throw 'Open XML validation failed'
            }
        } finally {
            $package.Dispose()
        }
    }
}

$word = New-Object -ComObject Word.Application
$security = $word.AutomationSecurity
try {
    $word.AutomationSecurity = 3
    $word.DisplayAlerts = 0
    foreach ($path in $paths) {
        $document = $word.Documents.Open($path, $false, $true, $false)
        try {
            $document.Repaginate()
            $columns = @(for ($i = 1; $i -le $document.Sections.Count; $i++) {
                $document.Sections.Item($i).PageSetup.TextColumns.Count
            })
            $starts = @(for ($i = 1; $i -le $document.Lists.Count; $i++) {
                $document.Lists.Item($i).ListParagraphs.Item(1).Range.ListFormat.ListValue
            })
            [pscustomobject]@{
                File = $document.Name
                Word = "$($word.Version) $($word.Build)"
                Pages = $document.ComputeStatistics(2)
                Columns = $columns -join ','
                Tables = $document.Tables.Count
                InlineShapes = $document.InlineShapes.Count
                ListStarts = $starts -join ','
            }
            if ($PreviewDirectory) {
                $pdf = Join-Path $PreviewDirectory ([IO.Path]::GetFileNameWithoutExtension($path) + '.pdf')
                if (Test-Path -LiteralPath $pdf) { throw "Preview already exists at $pdf" }
                $document.ExportAsFixedFormat($pdf, 17, $false, 0, 0, 1, 1, 0, $false, $true, 0, $false)
            }
        } finally {
            $document.Close(0)
        }
    }
} finally {
    $word.AutomationSecurity = $security
    $word.Quit([ref]0)
}
