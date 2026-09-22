-- E2E on Ironwood: normal $500, real queues and unmodified AI economy.
-- Human fixture buildings are healed; human workers are protected against one-shot kills.
-- AI economy, research costs and prerequisites remain unchanged.
local human,bot,tick=nil,nil,0
local seen={}
local function report(s) if not seen.failed then print('AGES V2: '..s);Media.DisplayMessage(s,'Ages test') end end
local function check(v,s) if not v then seen.failed=true;FatalError(s) end end
local function combat(owner)
 local enemy=Player.GetPlayer('Creeps')
 for i,kind in ipairs({'pikeman','archer','rider','musketeer','field.cannon'}) do
  local x,y=3+i*9,80
  local a=Actor.Create(kind,true,{Owner=owner,Location=CPos.New(x,y)})
  local target=Actor.Create('age.target',true,{Owner=enemy,Location=CPos.New(x,y+(kind=='field.cannon' and 11 or 8))})
  a.Stance='Defend'
  Trigger.OnDamaged(target,function(_,attacker,damage)
   if attacker~=a then return end
   local d=a.CenterPosition-target.CenterPosition;local dist=math.sqrt(d.X*d.X+d.Y*d.Y)
   if kind=='pikeman' or kind=='rider' then check(dist<=1400,'Melee dealt ranged damage')
   elseif kind=='archer' then check(dist>1500 and dist<=4200,'Archer range')
   elseif kind=='musketeer' then check(dist>1500 and dist<=5200,'Musket range')
   else check(dist>=1900 and dist<=9350,'Cannon range') end
   print('AGES HIT: '..kind..' damage='..damage..' distance='..dist)
  end)
  Trigger.AfterDelay(60,function() check(target.Health==target.MaxHealth,'Attack outside range');a.Attack(target) end)
  Trigger.AfterDelay(1200,function() check(target.IsDead,kind..' target survived');a.Destroy();report('PASS combat: '..kind) end)
 end
 for _,y in ipairs({24,49,74}) do
  local scout=Actor.Create('pikeman',true,{Owner=owner,Location=CPos.New(54,y)})
  scout.Move(CPos.New(76,y))
  Trigger.AfterDelay(750,function()
   check(scout.Location==CPos.New(76,y),'Blocked forest route '..y);scout.Destroy();report('PASS map route '..y)
  end)
 end
end
local function aggression(owner)
 local enemy=Player.GetPlayer('Creeps')
 for i,kind in ipairs({'pikeman','rider'}) do
  local a=Actor.Create(kind,true,{Owner=owner,Location=CPos.New(12+i*12,85)})
  local target=Actor.Create('e1',true,{Owner=enemy,Location=CPos.New(12+i*12,89)})
  check(a.Stance=='AttackAnything',kind..' default stance')
  target.Attack(a)
  Trigger.AfterDelay(900,function()
   check(not a.IsDead and target.IsDead,kind..' did not automatically chase and kill shooter')
   a.Destroy();report('PASS automatic melee pursuit: '..kind)
  end)
 end
end

WorldLoaded=function()
 Trigger.AfterDelay(25,function()
  human=Player.GetPlayer('Multi0');bot=Player.GetPlayer('Multi1')
  check(bot~=nil,'Missing AI')
  for _,p in ipairs({human,bot}) do
   check(#p.GetActorsByType('mhut.start')==1 and #p.GetActorsByType('mbarracks')==1,'Starting buildings')
   check(#p.GetActorsByType('worker')>=3,'Starting workers')
   check(not p.HasPrerequisites({'gunpowder.age'}) and not p.HasPrerequisites({'modern.age'}),'Age unlocked at start')
  end
  Camera.Position=human.GetActorsByType('mhut.start')[1].CenterPosition
  for _,a in ipairs(human.GetActorsByTypes({'mhut.start','mbarracks'})) do
   Trigger.OnDamaged(a,function(_,attacker,damage)
    if attacker and attacker.Owner==bot and not seen.aiAttack then seen.aiAttack=true;report('PASS AI attacks through Ironwood.') end
   end)
  end
  for _,a in ipairs(human.GetActorsByType('worker')) do a.GrantCondition('test-protected') end
  combat(human)
  Trigger.AfterDelay(1400,function() aggression(human) end)
  human.Build({'e1','musketeer','modern.age'})
  Trigger.AfterDelay(20,function()
   check(not human.IsProducing('e1') and not human.IsProducing('musketeer') and not human.IsProducing('modern.age'),'Bypassed era gates')
   check(human.Build({'pikeman','archer','rider','worker'},function(units)
    check(#units==4,'Medieval production');for _,a in ipairs(units) do if a.Type=='worker' then a.GrantCondition('test-protected') end end;seen.trained=true;report('PASS independent military/economy queues and paid medieval production.')
   end),'Cannot queue army')
  end)
 end)
end
Tick=function()
 tick=tick+1
 if not human then return end
 for _,a in ipairs(human.GetActorsByTypes({'mhut.start','mbarracks','worker'})) do a.Health=a.MaxHealth end
 if tick%250~=0 then return end
 local msg='tick='..tick..' workers='..#human.GetActorsByType('worker')..' human='..human.Cash..'+'..human.Resources..' AI='..bot.Cash..'+'..bot.Resources
 for _,kind in ipairs({'worker','pikeman','archer','rider','gunpowder.age','musketeer','field.cannon','modern.age','powr','proc','tent','barr','weap','e1'}) do
  local n=#bot.GetActorsByType(kind);if n>0 then seen[kind]=true;msg=msg..' '..kind..'='..n end
 end
 print('AGES STATE: '..msg)
 if human.Resources>0 and not seen.income then seen.income=true;report('PASS actual ore income.') end
 if seen.trained and not seen.gunpowderQueued and human.Cash+human.Resources>=1800 then
  seen.gunpowderQueued=true;check(human.Build({'gunpowder.age'}),'Cannot buy gunpowder')
 end
 if human.HasPrerequisites({'gunpowder.age'}) and not seen.gunpowderDone then
  seen.gunpowderDone=true;check(not human.HasPrerequisites({'modern.age'}),'Skipped middle era')
  report('PASS paid Gunpowder Age; industry still locked.')
  check(human.Build({'musketeer','field.cannon'},function(units)
   check(#units==2,'Gunpowder production');seen.powderArmy=true;report('PASS Musketeer and Field Cannon trained.')
  end),'Cannot produce gunpowder army')
 end
 if seen.powderArmy and not seen.modernQueued and human.Cash+human.Resources>=4500 then
  seen.modernQueued=true;check(human.Build({'modern.age'}),'Cannot buy industry')
 end
 if human.HasPrerequisites({'modern.age'}) and not seen.modernDone then
  seen.modernDone=true;report('PASS paid Industrial Age after Gunpowder.')
  check(human.Build({'e1'},function(units) check(#units==1,'Rifleman production');seen.rifle=true;report('PASS $200 Rifleman trained.') end),'Cannot queue Rifleman')
 end
 if not seen.complete and seen.rifle and seen.aiAttack and seen['gunpowder.age'] and seen.musketeer and seen['field.cannon'] and seen['modern.age'] and seen.powr and seen.proc and seen.e1 then
  seen.complete=true;report('PASS E2E COMPLETE: three eras, separate queues, Ironwood routes, combat and AI progression.')
 end
 if tick>=25000 and not seen.complete then check(false,'E2E timeout '..msg) end
end
