-- Append after villages.lua in an isolated Willowmere test map, fastest speed,
-- default $500, idle bot in Multi1. Does not alter the production map script.
local originalLoaded, originalTick = WorldLoaded, Tick
local p0,p1,neutral,worker,guard,invader,rider
local baseline,enemyBaseline
local scouts={}
local function check(ok,msg) if not ok then FatalError('VILLAGES: '..msg) end end
local function report(msg) print('VILLAGES PASS '..msg) end
local function unit(kind,p,x,y)
 local a=Actor.Create(kind,true,{Owner=p,Location=CPos.New(x,y)})
 if kind~='worker' then a.Stance='HoldFire' end
 a.Wait(10000)
 return a
end
WorldLoaded=function()
 originalLoaded()
 p0=Player.GetPlayer('Multi0');p1=Player.GetPlayer('Multi1');neutral=Player.GetPlayer('Neutral')
 Camera.Position=WestVillage.CenterPosition
end
Tick=function()
 originalTick()
 local t=DateTime.GameTime
 if t==25 then worker=unit('worker',p0,14,29) end
 if t==225 then
  check(WestVillage.Owner==neutral,'worker captured village')
  check(p0.Cash==500,'neutral village paid income')
  worker.Stop();worker.Destroy();report('worker excluded; neutral pays nothing')
 end
 if t==250 then guard=unit('pikeman',p0,14,29) end
 if t==400 then check(WestVillage.Owner==neutral,'capture completed before 8s') end
 if t==475 then
  check(WestVillage.Owner==p0,'pikeman capture failed');baseline=p0.Cash
  check(baseline==500,'unexpected instant capture bonus');report('8s infantry capture; owner changed without bonus')
 end
 if t==750 then
  check(p0.Cash==baseline+25,'income amount or cadence incorrect');baseline=p0.Cash
  report('exact $25 income after 10s')
 end
 if t==775 then invader=unit('pikeman',p1,15,29) end
 if t==1050 then
  check(WestVillage.Owner==p0,'contested village switched owner');check(p0.Cash==baseline,'contested village paid income')
  report('contest blocks capture and income');guard.Stop();guard.Destroy()
 end
 if t==1300 then
  check(WestVillage.Owner==p1,'enemy recapture failed');enemyBaseline=p1.Cash
  check(p0.Cash==baseline,'previous owner still receiving income');report('enemy recapture transfers ownership')
 end
 if t==1575 then
  check(p1.Cash==enemyBaseline+25,'new owner not paid');report('income paid only to new owner');invader.Stop();invader.Destroy()
  enemyBaseline=p1.Cash;rider=unit('rider',p0,59,38)
 end
 if t==1825 then
  check(WestVillage.Owner==p1,'empty village lost ownership')
  check(EastVillage.Owner==p0,'second village/cavalry capture failed')
  check(p1.Cash==enemyBaseline+25,'empty owned village stopped paying')
  report('persistent ownership; independent second village; cavalry capture')
  report('CAPTURE/INCOME COMPLETE')
 end
 if t==1850 then
  for i=1,6 do
   local a=Actor.Create('pikeman',true,{Owner=p1,Location=CPos.New(53+i%3,43+math.floor(i/3))})
   a.Stance='HoldFire';scouts[#scouts+1]=a
  end
 end
 if t==1925 then
  local moving=0
  for _,a in ipairs(scouts) do if not a.IsIdle then moving=moving+1 end end
  check(moving>=3,'bot did not dispatch a raid group')
  check(moving<=3,'bot committed more than half its army')
  report('bot sends a raid group and reserves half the army')
  report('E2E COMPLETE')
 end
end
