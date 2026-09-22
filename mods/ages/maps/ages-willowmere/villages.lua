-- Map-local objective: no special engineer, free capture bonus or extra win condition.
local troops = { pikeman=true, archer=true, rider=true, musketeer=true,
 e1=true, e2=true, e3=true, e4=true, shok=true }
local seconds = 0
local neutral
VillageStates = {}
local function eligible(a)
 return not a.IsDead and a.IsInWorld and not a.Owner.IsNonCombatant and troops[a.Type] == true
end
local function update(v)
 local present = {}
 for _,a in ipairs(Map.ActorsInCircle(v.flag.CenterPosition, WDist.New(5632), eligible)) do
  present[a.Owner.InternalName] = a.Owner
 end
 local count, visitor = 0,nil
 for _,p in pairs(present) do count=count+1;visitor=p end
 local hostile = count>1 or (count==1 and visitor~=v.flag.Owner)
 if count==1 and visitor~=v.flag.Owner then
  if v.claimant~=visitor then v.claimant=visitor;v.progress=0 end
  v.progress=v.progress+1
  Media.FloatingText(v.progress..'/8',v.flag.CenterPosition,25,visitor.Color)
  if v.progress>=8 then
   v.flag.Owner=visitor
   print('AGES_VILLAGE|'..DateTime.GameTime..'|event=capture|village='..v.name..'|owner='..visitor.InternalName)
   v.claimant=nil;v.progress=0;v.income=0
   Media.FloatingText('Village captured',v.flag.CenterPosition,75,visitor.Color)
   if visitor.IsLocalPlayer then Media.DisplayMessage(v.name..': +$25 / 10s','Village captured') end
  end
 else
  v.claimant=nil;v.progress=0
 end
 -- No income while contested or while an opponent is taking an empty village.
 if v.flag.Owner~=neutral and not hostile then
  v.income=v.income+1
  if v.income>=10 then
   v.flag.Owner.Cash=v.flag.Owner.Cash+25;v.income=0
   print('AGES_VILLAGE|'..DateTime.GameTime..'|event=payout|village='..v.name..'|owner='..v.flag.Owner.InternalName..'|amount=25')
   Media.FloatingText('+$25',v.flag.CenterPosition,40,v.flag.Owner.Color)
  end
 else v.income=0 end
 if seconds%5==0 then
  print('AGES_VILLAGE|'..DateTime.GameTime..'|event=state|village='..v.name..'|owner='..v.flag.Owner.InternalName..'|claimant='..(v.claimant and v.claimant.InternalName or 'none')..'|progress='..v.progress..'|hostile='..tostring(hostile)..'|income_clock='..v.income)
 end
end
WorldLoaded=function()
 neutral=Player.GetPlayer('Neutral')
 VillageStates={{flag=WestVillage,name='Westmere',progress=0,income=0},
                {flag=EastVillage,name='Eastmere',progress=0,income=0}}
 Trigger.AfterDelay(50,function()
  Media.DisplayMessage('Hold a village circle with combat troops for 8s. Each village earns $25 every 10s. Enemy troops interrupt capture and income.','Battle for Willowmere')
 end)
end
Tick=function()
 if DateTime.GameTime%25~=0 then return end
 seconds=seconds+1
 for _,v in ipairs(VillageStates) do update(v) end
 if seconds%5==0 then UpdateVillageAI(VillageStates,eligible,seconds) end
end
