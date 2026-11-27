param(
    [Parameter(Mandatory=$true)][string[]]$Document,
    [string]$PreviewDirectory,
    [string]$OpenXmlAssembly,
    [switch]$AccessibilityDetails
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
        $opened = $word.Documents.Open($path, $false, $true, $false)
        try {
            $opened.Repaginate()
            $columns = @(for ($i = 1; $i -le $opened.Sections.Count; $i++) {
                $opened.Sections.Item($i).PageSetup.TextColumns.Count
            })
            $starts = @(for ($i = 1; $i -le $opened.Lists.Count; $i++) {
                $opened.Lists.Item($i).ListParagraphs.Item(1).Range.ListFormat.ListValue
            })
            $summary = [ordered]@{
                File = $opened.Name
                Word = "$($word.Version) $($word.Build)"
                Pages = $opened.ComputeStatistics(2)
                Columns = $columns -join ','
                Tables = $opened.Tables.Count
                InlineShapes = $opened.InlineShapes.Count
                ListStarts = $starts -join ','
            }
            if ($AccessibilityDetails) {
                $summary.Outline = @(foreach ($paragraph in $opened.Paragraphs) {
                    $level = [int]$paragraph.OutlineLevel
                    if ($level -ge 1 -and $level -le 9) {
                        '{0} {1}' -f $level, $paragraph.Range.Text.Trim()
                    }
                })
                $summary.RepeatingHeaders = @(foreach ($table in $opened.Tables) {
                    $table.Rows.Item(1).HeadingFormat -eq -1
                })
                $summary.FigureDescriptions = @(foreach ($figure in $opened.InlineShapes) {
                    $figure.AlternativeText
                })
            }
            [pscustomobject]$summary
            if ($PreviewDirectory) {
                $pdf = Join-Path $PreviewDirectory ([IO.Path]::GetFileNameWithoutExtension($path) + '.pdf')
                if (Test-Path -LiteralPath $pdf) { throw "Preview already exists at $pdf" }
                $opened.ExportAsFixedFormat($pdf, 17, $false, 0, 0, 1, 1, 0, $false, $true, 0, $false)
            }
        } finally {
            $opened.Close(0)
        }
    }
} finally {
    $word.AutomationSecurity = $security
    $word.Quit([ref]0)
}
