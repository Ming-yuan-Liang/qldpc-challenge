$mine = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*qldpc-challenge\.venv*'} | Select-Object -First 2
foreach ($p in $mine) {
  Write-Output ("pid {0} start {1}" -f $p.Id, $p.StartTime)
  foreach ($t in ($p.Threads | Select-Object -First 6)) {
    Write-Output ("  tid {0} state {1} wait {2}" -f $t.Id, $t.ThreadState, $t.WaitReason)
  }
}
