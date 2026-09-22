-- Real production and AI on a skirmish map, starting with the normal $500.
local human, bot, trained, researched, income, tick = nil, nil, false, false, false, 0
local seen = {}
local function report(s) if seen.failed then return end; print('AGES TEST: ' .. s); Media.DisplayMessage(s, 'Ages test') end
local function check(v,s) if not v then seen.failed=true;FatalError(s) end end
local function combatTests(owner)
 local creeps=Player.GetPlayer('Creeps')
 local hits=0
 for i,kind in ipairs({'pikeman','archer','rider'}) do
  local y=5+i*4
  local unit=Actor.Create(kind,true,{Owner=owner,Location=CPos.New(26,y)})
  local target=Actor.Create('age.target',true,{Owner=creeps,Location=CPos.New(31,y)})
  unit.Stance='Defend'
  Trigger.OnDamaged(target,function(_,attacker,damage)
   check(attacker==unit,'Unexpected combat-test attacker')
   local d=unit.CenterPosition-target.CenterPosition
   local distance=math.sqrt(d.X*d.X+d.Y*d.Y)
   if kind=='archer' then check(distance>1500 and distance<=4200,'Archer range invalid')
   else check(distance<=1400,'Melee unit dealt ranged damage') end
   hits=hits+1
   print('AGES COMBAT: '..kind..' damage='..damage..' distance='..distance)
  end)
  Trigger.AfterDelay(60,function()
   check(target.Health==target.MaxHealth,kind..' damaged a target five cells away while holding')
   unit.Attack(target)
  end)
  Trigger.AfterDelay(650,function()
   check(target.IsDead,kind..' did not kill combat target')
   unit.Destroy()
   report('PASS: '..kind..' combat range and damage.')
  end)
 end
 local pike=Actor.Create('pikeman',true,{Owner=owner,Location=CPos.New(38,8)})
 local air=Actor.Create('tran',true,{Owner=creeps,CenterPosition=pike.CenterPosition+WVec.New(1024,0,Actor.CruiseAltitude('tran'))})
 pike.Attack(air)
 Trigger.AfterDelay(100,function()
  check(air.Health==air.MaxHealth,'Pikeman damaged airborne target');air.Destroy();pike.Destroy()
  report('PASS: pikeman cannot damage airborne targets.')
 end)
end

WorldLoaded = function()
 Trigger.AfterDelay(25, function()
  human=Player.GetPlayer('Multi0');bot=Player.GetPlayer('Multi1')
  for _,p in ipairs({human,bot}) do
   check(#p.GetActorsByType('mhut.start')==1 and #p.GetActorsByType('mbarracks')==1,'Wrong starting buildings')
   check(#p.GetActorsByType('worker')>=3,'Missing workers')
   check(#p.GetActorsByType('mcv')==0,'Unexpected MCV')
   check(not p.HasPrerequisites({'modern.age'}),'Modern age starts unlocked')
  end
  for _,a in ipairs(human.GetActorsByTypes({'mhut.start','mbarracks'})) do
   Trigger.OnDamaged(a,function(_,attacker,damage)
    if attacker and attacker.Owner==bot and not seen.aiAttack then seen.aiAttack=true;report('PASS: AI attacks the enemy base.') end
   end)
  end
  combatTests(human)
  Camera.Position=human.GetActorsByType('mhut.start')[1].CenterPosition
  report('PASS: medieval start and modern age locked.')
  human.Build({'e1'})
  Trigger.AfterDelay(20,function()
   check(not human.IsProducing('e1'),'Modern soldier queued before age upgrade')
   check(human.Build({'pikeman','archer','rider','worker'},function(units)
    check(#units==4,'Not all medieval units produced');trained=true
    report('PASS: trained Pikeman, Archer, Rider and Gatherer via normal production.')
   end),'Cannot queue medieval units')
  end)
  for _,worker in ipairs(human.GetActorsByType('worker')) do worker.FindResources() end
 end)
end
Tick = function()
 tick=tick+1
 if not human then return end
 for _,a in ipairs(human.GetActorsByTypes({'mhut','mhut.start','mbarracks'})) do a.Health=a.MaxHealth end
 if tick%250~=0 then return end
 local types={'worker','pikeman','archer','rider','modern.age','powr','proc','barr','tent','e1','weap','3tnk'}
 local msg='tick='..tick..' human='..human.Cash..'+'..human.Resources..' AI='..bot.Cash..'+'..bot.Resources
 for _,t in ipairs(types) do
  local n=#bot.GetActorsByType(t);if n>0 then seen[t]=true;msg=msg..' '..t..'='..n end
 end
 print('AGES STATE: '..msg)
 -- Keep the human test fixture alive while waiting for the AI's natural economy.
 for _,a in ipairs(human.GetActorsByTypes({'mhut','mhut.start','mbarracks'})) do a.Health=a.MaxHealth end
 if not income and human.Resources>0 then income=true;report('PASS: Gatherers deposited harvested ore at the Gathering Hut.') end
 if trained and not researched and human.Cash+human.Resources>=3000 and not human.IsProducing('modern.age') then
  researched=true;report('Researching modern age from naturally harvested income.')
  check(human.Build({'modern.age'}),'Cannot queue age upgrade')
 end
 if human.HasPrerequisites({'modern.age'}) and not seen.humanModern then
  seen.humanModern=true;report('PASS: paid age upgrade completed, modern prerequisite granted.')
  check(human.Build({'e1'},function(units) check(#units==1,'Modern production failed');report('PASS: modern soldier trained after age upgrade.');seen.humanE1=true end),'Cannot queue modern infantry')
 end
 if seen['modern.age'] and not seen.aiAge then seen.aiAge=true;report('PASS: AI bought the modern age using its own economy.') end
 if seen.humanE1 and seen.aiAge and seen.aiAttack and seen.pikeman and seen.archer and seen.rider and seen.powr and (seen.barr or seen.tent or seen.weap) and seen.e1 and not seen.complete then
  seen.complete=true;report('PASS: E2E COMPLETE - both economies, medieval production, paid age upgrades, AI modern buildings and soldiers.')
 end
 if tick>=20000 and not seen.complete then FatalError('E2E timed out: '..msg) end
end
