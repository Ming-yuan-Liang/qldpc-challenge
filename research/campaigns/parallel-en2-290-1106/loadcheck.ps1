$sample1 = Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor -Filter "Name='_Total'" | Select-Object -ExpandProperty PercentProcessorTime
$p = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*qldpc-challenge*'} | Select-Object -First 3
$ids = $p.Id
$cpu1 = @{}
foreach ($x in $p) { $cpu1[$x.Id] = $x.CPU }
Start-Sleep -Seconds 20
$sample2 = Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor -Filter "Name='_Total'" | Select-Object -ExpandProperty PercentProcessorTime
Write-Output ("cpu_total_pct {0} then {1}" -f $sample1, $sample2)
foreach ($id in $ids) {
  $y = Get-Process -Id $id -ErrorAction SilentlyContinue
  if ($y) { Write-Output ("pid {0} cpu {1} -> {2} delta {3}" -f $id, [math]::Round($cpu1[$id],1), [math]::Round($y.CPU,1), [math]::Round($y.CPU-$cpu1[$id],1)) }
}
