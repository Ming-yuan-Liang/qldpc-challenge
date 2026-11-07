$ws = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object {$_.CommandLine -like '*phase_deep_ckpt*'}
$live=@{}
foreach ($w in $ws) { $p=Get-Process -Id $w.ProcessId -ErrorAction SilentlyContinue; if ($p -and $p.CPU -gt 1) { $live[$w.ProcessId]=$p.CPU } }
$s=($live.Values | Measure-Object -Sum).Sum
Start-Sleep -Seconds 30
$s2=0
foreach ($id in @($live.Keys)) { $p=Get-Process -Id $id -ErrorAction SilentlyContinue; if ($p) { $s2+=$p.CPU } }
Write-Output ("live_workers {0} cpu_sum {1} -> {2} delta_30s {3}" -f $live.Count, [math]::Round($s,1), [math]::Round($s2,1), [math]::Round($s2-$s,1))
