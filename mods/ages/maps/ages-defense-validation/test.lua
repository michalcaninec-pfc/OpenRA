-- Dedicated defense placement regression. $5000 fixture cash, scripted age
-- tokens after medieval checks; buildings use actual paid queues and placement.
local bot,human,tick,upgraded,complete=nil,nil,0,false,false
local towerTarget=nil
local hit=false
local function check(v,s) if not v then FatalError(s) end end
local function report(s) print('AGES DEFENSES: '..s);Media.DisplayMessage(s,'Defense test') end
WorldLoaded=function()
 Trigger.AfterDelay(25,function()
  bot=Player.GetPlayer('Multi1');human=Player.GetPlayer('Multi0')
  check(not bot.HasPrerequisites({'fact'}),'Hut acts as conyard before Industry')
  check(#bot.GetActorsByType('fact')==0,'Unexpected construction yard')
  Camera.Position=bot.GetActorsByType('mhut.start')[1].CenterPosition
 end)
end
Tick=function()
 tick=tick+1
 if not bot or tick%100~=0 then return end
 local towers=bot.GetActorsByType('watchtower')
 local walls=bot.GetActorsByType('palisade')
 print('DEFENSE STATE '..tick..' tower='..#towers..' palisade='..#walls..' brik='..#bot.GetActorsByType('brik')..' ftur='..#bot.GetActorsByType('ftur')..' cash='..bot.Cash)
 if #towers>0 and not towerTarget then
  local tower=towers[1]
  towerTarget=Actor.Create('age.target',true,{Owner=Player.GetPlayer('Creeps'),Location=tower.Location+CVec.New(0,5)})
  Trigger.OnDamaged(towerTarget,function(_,attacker,damage)
   if attacker==tower and damage>0 then hit=true end
  end)
  report('PASS watchtower built through normal production and placement.')
 end
 if not upgraded and #towers>0 and #walls>=3 and towerTarget.IsDead and hit then
  check(bot.Cash<5000,'Defense construction did not spend cash')
  report('PASS paid palisades and automatic watchtower arrow combat.')
  upgraded=true
  Actor.Create('gunpowder.age',true,{Owner=bot})
  Actor.Create('modern.age',true,{Owner=bot})
  Trigger.AfterDelay(50,function()
   check(bot.HasPrerequisites({'fact'}),'Starting hut did not unlock conyard prerequisite')
   check(not human.HasPrerequisites({'fact'}),'Industrial conyard leaked to other player')
   check(#bot.GetActorsByType('fact')==0,'Test accidentally created real conyard')
   report('PASS existing starting hut automatically provides construction yard after Industry.')
  end)
 end
 if upgraded and #bot.GetActorsByType('brik')>=2 and #bot.GetActorsByType('ftur')>=1 and not complete then
  complete=true;report('PASS DEFENSE E2E COMPLETE: medieval tower/walls and modern walls/flame turret constructed without a separate conyard.')
 end
 if tick>=6000 and not complete then check(false,'Defense placement timeout') end
end
