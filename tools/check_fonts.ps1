param([Parameter(Mandatory=$true)][ValidateCount(1,16)][string[]]$Family)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName PresentationCore

# These samples cover the benchmark scripts, digits, SQL punctuation and a few technical signs.
$samples = @{
    Latin = [int[]][char[]]'AZaz'
    Cyrillic = @(0x0401, 0x0410, 0x042F, 0x0430, 0x044F, 0x0451)
    Digits = (0x0030..0x0039)
    Code = [int[]][char[]]'_<>=.,;()[]+-'
    Technical = @(0x00B7, 0x00D7, 0x2192, 0x2193, 0x2212, 0x2264)
}
$installed = [Windows.Media.Fonts]::SystemFontFamilies
foreach ($name in $Family) {
    $wpfFamily = if ($name -eq 'Arial Black') { 'Arial' } else { $name }
    $matched = @($installed | Where-Object { $_.FamilyNames.Values -contains $wpfFamily })
    $weights = if ($name -eq 'Arial Black') { @([Windows.FontWeights]::Black) } else {
        @([Windows.FontWeights]::Normal, [Windows.FontWeights]::Bold)
    }
    foreach ($weight in $weights) {
        $glyph = $null
        $face = $matched | ForEach-Object { $_.GetTypefaces() } | Where-Object {
            $_.Weight -eq $weight -and $_.Style -eq [Windows.FontStyles]::Normal -and
            $_.Stretch -eq [Windows.FontStretches]::Normal
        } | Select-Object -First 1
        $found = $null -ne $face -and $face.TryGetGlyphTypeface([ref]$glyph) -and
            $glyph.StyleSimulations -eq [Windows.Media.StyleSimulations]::None -and
            ($name -eq $wpfFamily -or $glyph.Win32FamilyNames.Values -contains $name)
        $missing = [ordered]@{}
        if ($found) {
            foreach ($category in @('Latin','Cyrillic','Digits','Code','Technical')) {
                $missing[$category] = @($samples[$category] | Where-Object {
                    !$glyph.CharacterToGlyphMap.ContainsKey($_) -or !$glyph.CharacterToGlyphMap[$_]
                } | ForEach-Object { 'U+{0:X4}' -f $_ })
            }
        }
        [pscustomobject]@{
            Family = $name
            Weight = $weight.ToString()
            Available = $found
            Version = $(if ($found) { $glyph.VersionStrings.Values | Select-Object -First 1 })
            Embedding = $(if ($found) { $glyph.EmbeddingRights.ToString() })
            MissingSample = $missing
        }
    }
}
