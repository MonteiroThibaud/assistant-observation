# Telechargement des photos du ciel profond des objets ajoutes en 0.89 (Digitized Sky Survey) pour l'Assistant d'observation.
# Windows : lance simplement "Lancer-Windows.bat" (double-clic). Rien a installer.
# Source : SkyView (NASA), qui distribue le Digitized Sky Survey (STScI, subvention NAG W-2166).
$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}
$base = if ($env:DSS_URL) { $env:DSS_URL } else { 'https://skyview.gsfc.nasa.gov/current/cgi/pskcall' }
$dossier = Join-Path $PSScriptRoot 'dss_images'
New-Item -ItemType Directory -Force -Path $dossier | Out-Null

# identifiant, ascension droite (deg), declinaison (deg), champ de la photo (deg)
$objets = @(
    @('NGC 1788',76.7217,-3.341,0.3),
    @('NGC 2175',92.4148,20.4876,1.2),
    @('NGC 6823',295.791,23.2999,0.3),
    @('NGC 7380',341.837,58.1324,0.75),
    @('NGC 2071',86.7803,0.2943,0.3),
    @('NGC 3521',166.452,-0.0359,0.3),
    @('NGC 6818',295.99,-14.1532,0.3),
    @('NGC 4697',192.149,-5.8007,0.3),
    @('NGC 4725',192.611,25.5008,0.3),
    @('NGC 2440',115.481,-18.2085,0.3),
    @('NGC 4365',186.118,7.3177,0.3),
    @('NGC 1023',40.1,39.0633,0.3),
    @('NGC 1999',84.1056,-6.7159,0.3),
    @('NGC 4526',188.513,7.6995,0.3),
    @('NGC 1535',63.5657,-12.7394,0.3),
    @('NGC 2683',133.172,33.4217,0.3),
    @('NGC 4490',187.651,41.6439,0.3),
    @('NGC 4214',183.913,36.3269,0.3),
    @('NGC 3184',154.57,41.4241,0.3),
    @('NGC 2768',137.906,60.0372,0.3),
    @('NGC 3077',150.829,68.7339,0.3),
    @('NGC 4535',188.585,8.1978,0.3),
    @('NGC 4559',188.99,27.96,0.32),
    @('NGC 4216',183.977,13.1494,0.3),
    @('NGC 5248',204.383,8.8852,0.3),
    @('NGC 1555',65.4976,19.5352,0.3),
    @('NGC 3344',160.88,24.9222,0.3),
    @('NGC 6822',296.241,-14.8034,0.52),
    @('NGC 1931',82.8556,34.2466,0.3),
    @('NGC 3953',178.454,52.3268,0.3),
    @('NGC 6503',267.36,70.1444,0.3),
    @('NGC 925',36.8203,33.5792,0.32),
    @('NGC 2976',146.814,67.9164,0.3),
    @('NGC 2841',140.511,50.9765,0.3),
    @('NGC 4414',186.613,31.2235,0.3),
    @('NGC 2775',137.584,7.0379,0.3),
    @('NGC 6891',303.787,12.7044,0.3),
    @('NGC 7814',0.812,16.1454,0.3),
    @('NGC 5033',198.364,36.5939,0.3),
    @('NGC 7008',315.137,54.5432,0.3),
    @('NGC 3079',150.491,55.6798,0.3),
    @('NGC 5005',197.734,37.0592,0.3),
    @('NGC 2438',115.46,-14.7358,0.3),
    @('NGC 246',11.764,-11.8719,0.3),
    @('NGC 4361',186.128,-18.7848,0.3),
    @('NGC 6884',302.599,46.4608,0.3),
    @('NGC 7026',316.577,47.8522,0.3),
    @('NGC 4438',186.94,13.0088,0.3),
    @('NGC 4435',186.919,13.0789,0.3),
    @('NGC 3626',170.016,18.3568,0.3),
    @('NGC 6905',305.596,20.1045,0.3),
    @('NGC 2371',111.394,29.4906,0.3),
    @('NGC 6369',262.335,-23.7594,0.3),
    @('NGC 1501',61.7474,60.9207,0.3),
    @('NGC 4485',187.63,41.7012,0.3),
    @('IC 5146',328.37,47.2669,0.3),
    @('IC 405',79.1228,34.3562,1.5)
)

function Test-Jpeg($chemin) {
    if (-not (Test-Path $chemin)) { return $false }
    $b = [IO.File]::ReadAllBytes($chemin)
    return ($b.Length -gt 3000 -and $b[0] -eq 255 -and $b[1] -eq 216 -and $b[2] -eq 255)
}

$index = @()
$echecs = @()
$n = 0
foreach ($o in $objets) {
    $n++
    $id = $o[0]; $ra = $o[1]; $dec = $o[2]; $champ = $o[3]
    $fichier = ($id -replace ' ', '_') + '.jpg'
    $chemin = Join-Path $dossier $fichier
    $ok = Test-Jpeg $chemin
    $etat = 'deja la'
    if (-not $ok) {
        $url = "${base}?Position=${ra},${dec}&Survey=DSS&Size=${champ}&Pixels=512&Coordinates=J2000&Return=JPEG"
        $etat = 'ECHEC'
        for ($k = 1; $k -le 4 -and -not $ok; $k++) {
            try {
                Invoke-WebRequest -Uri $url -OutFile $chemin -UserAgent 'assistant-observation/1.0' -TimeoutSec 90 -UseBasicParsing
                $ok = Test-Jpeg $chemin
                if (-not $ok) { Remove-Item $chemin -ErrorAction SilentlyContinue; $etat = 'ECHEC : reponse inattendue' }
            } catch {
                $etat = 'ECHEC : ' + $_.Exception.Message
                Remove-Item $chemin -ErrorAction SilentlyContinue
            }
            if (-not $ok) { Start-Sleep -Seconds (3 * $k) }
        }
        if ($ok) { $etat = 'ok' }
        Start-Sleep -Seconds 1
    }
    Write-Host ("[{0,3}/{1}] {2,-10} champ {3} deg : {4}" -f $n, $objets.Count, $id, $champ, $etat)
    if ($ok) {
        $index += [pscustomobject]@{ id = $id; fichier = $fichier; ra = $ra; dec = $dec; champ = $champ; pixels = 512 }
    } else { $echecs += $id }
}
$json = if ($index.Count -eq 0) { '[]' } else { ConvertTo-Json -InputObject @($index) }
$json | Set-Content -Path (Join-Path $dossier 'index.json') -Encoding UTF8
Write-Host ''
Write-Host ("Termine : {0} photos dans {1}" -f $index.Count, $dossier)
if ($echecs.Count -gt 0) { Write-Host ('Objets en echec (relance pour reessayer) : ' + ($echecs -join ', ')) }
