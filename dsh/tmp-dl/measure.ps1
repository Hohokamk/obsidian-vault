$ErrorActionPreference = 'Continue'
$out = Join-Path $PSScriptRoot '.'
New-Item -ItemType Directory -Force -Path $out | Out-Null
foreach ($pkg in @('dsh-pet', 'billion-context')) {
  $meta = & curl.exe -s --max-time 60 "https://registry.npmjs.org/$pkg"
  if (-not $meta) { Write-Output ("{0}: metadata fetch returned nothing" -f $pkg); continue }
  $j = $meta | ConvertFrom-Json
  $v = $j.'dist-tags'.latest
  $u = $j.versions.$v.dist.tarball
  $target = Join-Path $out ($pkg + '.tgz')
  $fmt = '%{size_download} %{speed_download} %{time_total} %{http_code}'
  $r = & curl.exe -sL --max-time 300 -o $target -w $fmt $u
  $unpacked = $j.versions.$v.dist.unpackedSize
  Write-Output ("{0}: latest={1} tarball={2} speed/size/time/code=[{3}] unpackedSize={4}" -f $pkg, $v, $u, $r, $unpacked)
}
