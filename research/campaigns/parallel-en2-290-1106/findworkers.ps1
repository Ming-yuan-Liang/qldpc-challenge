$ws = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object {$_.CommandLine -like '*phase_deep_ckpt*'}
Write-Output ("workers {0}" -f $ws.Count)
foreach ($w in $ws) {
  $p = Get-Process -Id $w.ProcessId -ErrorAction SilentlyContinue
  Write-Output ("pid {0} created {1} cpu {2}" -f $w.ProcessId, $w.CreationDate.ToString('HH:mm:ss'), [math]::Round($p.CPU,1))
}
