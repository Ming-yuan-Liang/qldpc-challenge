$a=(Get-Process python -ErrorAction SilentlyContinue | Measure-Object CPU -Sum).Sum
$c=(Get-Process python -ErrorAction SilentlyContinue).Count
Start-Sleep -Seconds 45
$b=(Get-Process python -ErrorAction SilentlyContinue | Measure-Object CPU -Sum).Sum
$c2=(Get-Process python -ErrorAction SilentlyContinue).Count
Write-Output ("pyprocs {0} -> {1}  cpu_sum_delta_45s {2}" -f $c, $c2, [math]::Round($b-$a,1))
