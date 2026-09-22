-- Visual regression fixture: use instead of the village scripts in a copied map.
-- Fog enabled and locked, explored map disabled. Observe initial shroud, partial
-- vision after tick 250, and explored fog after tick 800. Do not enable capture.
local scout
WorldLoaded=function()
 Camera.Position=EastVillage.CenterPosition
 print('FOG CHECK: initially unrevealed; no village ring should appear')
end
Tick=function()
 local t=DateTime.GameTime
 if t==250 then
  scout=Actor.Create('pikeman',true,{Owner=Player.GetPlayer('Multi0'),Location=CPos.New(59,40)})
  scout.Stance='HoldFire';scout.Wait(10000)
  print('FOG CHECK: visible center; ring clipped at sight boundary')
 end
 if t==800 then
  scout.Stop();scout.Destroy()
  print('FOG CHECK: explored but no current vision; ring should disappear')
 end
end
