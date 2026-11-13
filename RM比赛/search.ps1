function Search-Bing($q, $n=10) {
  $ProgressPreference='SilentlyContinue'
  $u = "https://www.bing.com/search?q=" + [uri]::EscapeDataString($q) + "&setlang=zh-CN&count=20"
  $r = Invoke-WebRequest -Uri $u -UserAgent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' -TimeoutSec 30
  $html = $r.Content
  $matches = [regex]::Matches($html, '(?s)<li class="b_algo".*?</li>')
  $i=0
  foreach($m in $matches){
    $i++; if($i -gt $n){break}
    $t = [regex]::Match($m.Value,'(?s)<h2>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>')
    if($t.Success){
      $href=$t.Groups[1].Value
      $title=([regex]::Replace($t.Groups[2].Value,'<[^>]+>',''))
      $snippet=''
      $sm=[regex]::Match($m.Value,'(?s)<p[^>]*>(.*?)</p>')
      if($sm.Success){$snippet=[regex]::Replace($sm.Groups[1].Value,'<[^>]+>','')}
      Write-Output ("{0}. {1}`n   {2}`n   {3}" -f $i,$title.Trim(),$href,$snippet.Trim())
    }
  }
}
Search-Bing 'RMUC 2027 重装机器人' 12
'===== 2 ====='
Search-Bing 'RoboMaster 2027 重装机器人 规则 解析' 12
'===== 3 ====='
Search-Bing 'RoboMaster 2027 赛季 规则 重装 42mm' 12
