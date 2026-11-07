$mine = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*qldpc-challenge*'}
$a = ($mine | Measure-Object CPU -Sum).Sum
Start-Sleep -Seconds 30
$mine2 = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*qldpc-challenge*'}
$b = ($mine2 | Measure-Object CPU -Sum).Sum
Write-Output ("repo_py_count {0} cpu_delta_30s {1}" -f $mine2.Count, [math]::Round($b-$a,1))
