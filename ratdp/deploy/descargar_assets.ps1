<#
  descargar_assets.ps1
  --------------------
  Descarga Bootstrap 5.3 a static/css/vendor y static/js/vendor.

  Motivo: la aplicación NO enlaza a un CDN externo. En un sistema que trata
  datos personales, cargar recursos desde un tercero implica que ese tercero
  observa la IP y el user-agent de cada usuario del sistema en cada carga de
  página, lo que constituye una comunicación de datos no declarada en el RAT.
  Servir los estáticos localmente evita esa dependencia y permite operar en
  redes internas sin salida a internet.

  Ejecutar UNA VEZ desde una máquina con internet, y versionar/copiar los
  archivos resultantes al servidor.
#>
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
$css  = Join-Path $raiz "static\css\vendor"
$js   = Join-Path $raiz "static\js\vendor"
New-Item -ItemType Directory -Force -Path $css, $js | Out-Null

$version = "5.3.3"
$base = "https://cdn.jsdelivr.net/npm/bootstrap@$version/dist"

Invoke-WebRequest "$base/css/bootstrap.min.css"      -OutFile (Join-Path $css "bootstrap.min.css")
Invoke-WebRequest "$base/js/bootstrap.bundle.min.js" -OutFile (Join-Path $js  "bootstrap.bundle.min.js")

Write-Host "Bootstrap $version descargado." -ForegroundColor Green
Write-Host "Verifique el hash SHA-256 de cada archivo contra el publicado por el proyecto."
Get-FileHash (Join-Path $css "bootstrap.min.css")      -Algorithm SHA256
Get-FileHash (Join-Path $js  "bootstrap.bundle.min.js") -Algorithm SHA256
