# Gera o banner do perfil e as capas dos repositórios a partir de brand/_source/render.html.
# Requisito: Microsoft Edge. Opcional: Python com Pillow (reduz o tamanho dos PNG sem perda visível).
# Uso (na raiz do repositório):  powershell -NoProfile -File .\brand\render.ps1

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$edge = "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
$src  = (Resolve-Path "$PSScriptRoot\_source\render.html").Path -replace '\\','/'
$out  = Join-Path $root 'assets'
New-Item -ItemType Directory -Force "$out\covers", "$out\hero" | Out-Null

# O topo do README (banner, botões, painel) fica em assets/hero.
$jobs = @(
  @{ id='banner'; size='1280,300'; file="$out\hero\banner.png" },
  @{ id='banner-mobile'; size='720,400'; file="$out\hero\banner-mobile.png" }
) + (@('lab-active-directory','kaizen-tech','campus-ai','fleet-report-demo','inclusao-360','portfolio') | ForEach-Object {
  @{ id=$_; size='1280,640'; file="$out\covers\$_.png" }
})

$ErrorActionPreference = 'Continue'   # o Edge escreve avisos inofensivos no stderr
foreach ($j in $jobs) {
  Remove-Item $j.file -ErrorAction SilentlyContinue
  $edgeArgs = @('--headless=new','--hide-scrollbars','--force-device-scale-factor=2',
            '--default-background-color=00000000',"--window-size=$($j.size)",'--virtual-time-budget=6000',
            "--screenshot=$($j.file)","file:///$src`?id=$($j.id)")
  Start-Process -FilePath $edge -ArgumentList $edgeArgs -Wait -WindowStyle Hidden
  if (Test-Path $j.file) { Write-Host "ok     $($j.file)" } else { Write-Host "FALHOU $($j.file)" }
}

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
  & py -c @"
import glob, os
try:
    from PIL import Image
except ImportError:
    raise SystemExit('Pillow ausente: PNG mantidos sem otimização')
for f in glob.glob(r'$out\hero\banner*.png') + glob.glob(r'$out\covers\*.png'):
    im = Image.open(f).convert('RGBA')
    im.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(f, optimize=True)
    print(f'{os.path.getsize(f)//1024:>4} KB  {f}')
"@
}
