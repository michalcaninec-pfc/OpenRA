-- Objective decisions complement the normal Ages economy and army AI.
-- Only idle troops receive orders; at least half the army stays available
-- for normal squads. Known objective ownership is public, enemy army counts
-- are inspected only near friendly troops or a friendly village.
local cooldown = {}
local function distance(a,b)
 local dx=a.X-b.X;local dy=a.Y-b.Y
 return dx*dx+dy*dy
end
function UpdateVillageAI(states,eligible,seconds)
 for _,p in ipairs(Player.GetPlayers(function(p) return p.IsBot and not p.IsNonCombatant end)) do
  local army=p.GetGroundAttackers()
  local available={}
  local guard={}
  -- Keep one nearby idle capturer at each owned objective when possible.
  for _,v in ipairs(states) do
   if v.flag.Owner==p then
    for _,a in ipairs(army) do
     if eligible(a) and a.IsIdle and distance(a.Location,v.flag.Location)<=30 then guard[a]=true;break end
    end
   end
  end
  for _,a in ipairs(army) do
   if eligible(a) and a.IsIdle and not guard[a] then available[#available+1]=a end
  end
  local budget=math.min(#available,math.max(1,math.floor(#army/2)))
  local best,bestScore,bestNeed,bestKind=nil,-math.huge,0,nil
  for _,v in ipairs(states) do
   local key=p.InternalName..v.name
   if seconds>=(cooldown[key] or 0) then
    local friendly=0
    for _,a in ipairs(army) do if distance(a.Location,v.flag.Location)<=49 then friendly=friendly+1 end end
    local enemy=0
    if friendly>0 or v.flag.Owner==p then
     for _,a in ipairs(Map.ActorsInCircle(v.flag.CenterPosition,WDist.New(5632),eligible)) do
      if not a.Owner.IsAlliedWith(p) then enemy=enemy+1 end
     end
    end
    local kind,need,score=nil,0,0
    if v.flag.Owner==p and enemy>0 then
     kind='defend';need=math.min(4,math.max(2,enemy+1-friendly));score=1000
    elseif v.flag.Owner.IsNonCombatant then
     kind='capture';need=enemy>0 and math.max(3,enemy+1) or 1;score=500
    elseif not v.flag.Owner.IsAlliedWith(p) then
     kind='raid';need=math.max(3,enemy+1-friendly);score=250
    end
    if seconds%15==0 then
     local reason=not kind and 'no_target' or (budget<need and 'insufficient_idle_budget' or 'eligible')
     print('AGES_AI|'..DateTime.GameTime..'|event=candidate|player='..p.InternalName..'|village='..v.name..'|reason='..reason..'|need='..need..'|budget='..budget..'|army='..#army..'|available='..#available..'|friendly='..friendly..'|enemy='..enemy)
    end
    if kind and budget>=need then
     local nearest=math.huge
     for _,a in ipairs(available) do nearest=math.min(nearest,distance(a.Location,v.flag.Location)) end
     score=score-math.sqrt(nearest)
     if score>bestScore then best=v;bestScore=score;bestNeed=need;bestKind=kind end
    end
   elseif seconds%15==0 then
    print('AGES_AI|'..DateTime.GameTime..'|event=candidate|player='..p.InternalName..'|village='..v.name..'|reason=cooldown|budget='..budget..'|army='..#army..'|available='..#available)
   end
  end
  if best then
   table.sort(available,function(a,b) return distance(a.Location,best.flag.Location)<distance(b.Location,best.flag.Location) end)
   local count=math.min(budget,math.max(bestNeed,bestKind=='capture' and 2 or 3))
   local dispatched={}
   for i=1,count do
    dispatched[#dispatched+1]=tostring(available[i].ActorID)
    available[i].AttackMove(best.flag.Location+CVec.New(0,1))
   end
   cooldown[p.InternalName..best.name]=seconds+20
   print('AGES_AI|'..DateTime.GameTime..'|event=dispatch|player='..p.InternalName..'|village='..best.name..'|action='..bestKind..'|count='..count..'|army='..#army..'|available='..#available..'|budget='..budget..'|units='..table.concat(dispatched,',')..'|target_x='..best.flag.Location.X..'|target_y='..best.flag.Location.Y)
   print('VILLAGE AI '..p.InternalName..' '..bestKind..' '..best.name..' troops='..count)
  end
 end
end
