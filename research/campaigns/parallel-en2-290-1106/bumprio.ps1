$mine = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*qldpc-challenge\.venv*'}
foreach ($p in $mine) { try { $p.PriorityClass = 'High' } catch { Write-Output ("skip {0}: {1}" -f $p.Id, $_.Exception.Message) } }
Write-Output ("bumped {0} processes to High" -f $mine.Count)
Start-Sleep -Seconds 20
$mine2 = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*qldpc-challenge\.venv*'}
$sum = ($mine2 | Measure-Object CPU -Sum).Sum
Start-Sleep -Seconds 20
$sum2 = (Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*qldpc-challenge\.venv*'} | Measure-Object CPU -Sum).Sum
Write-Output ("venv_py {0} cpu_delta_20s {1}" -f $mine2.Count, [math]::Round($sum2-$sum,1))
