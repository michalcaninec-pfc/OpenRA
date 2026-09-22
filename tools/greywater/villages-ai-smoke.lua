-- Isolated real-engine checks of the objective planner. Load after villages.lua.
local setup=WorldLoaded
local p0,p1,enemy
local army={}
local function eligible(a) return not a.IsDead and a.IsInWorld and a.Type=='pikeman' end
local function check(n,label)
 local busy=0
 for _,a in ipairs(army) do if not a.IsIdle then busy=busy+1 end end
 if busy~=n then FatalError('AI '..label..': expected '..n..' dispatched, got '..busy) end
 print('VILLAGE AI TEST PASS '..label..' dispatched='..busy..' reserve='..(#army-busy))
end
local function stop() for _,a in ipairs(army) do a.Stop() end end
WorldLoaded=function()
 setup();p0=Player.GetPlayer('Multi0');p1=Player.GetPlayer('Multi1')
 for i=1,6 do
  local a=Actor.Create('pikeman',true,{Owner=p1,Location=CPos.New(53+i%3,43+math.floor(i/3))})
  a.Stance='HoldFire';army[#army+1]=a
 end
end
Tick=function()
 local t=DateTime.GameTime
 if t==25 then UpdateVillageAI(VillageStates,eligible,100) end
 if t==30 then check(2,'nearest neutral capture');stop();WestVillage.Owner=p1;EastVillage.Owner=p0 end
 if t==40 then enemy=Actor.Create('pikeman',true,{Owner=p0,Location=CPos.New(14,29)});enemy.Stance='HoldFire';enemy.Wait(10000) end
 if t==50 then UpdateVillageAI(VillageStates,eligible,130) end
 if t==55 then check(3,'defense takes priority over enemy raid');stop();enemy.Stop();enemy.Destroy() end
 if t==75 then UpdateVillageAI(VillageStates,eligible,160) end
 if t==80 then check(3,'group raid with reserve');print('VILLAGE AI TEST E2E COMPLETE') end
end
