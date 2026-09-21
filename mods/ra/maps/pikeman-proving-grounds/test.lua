-- Repeatable smoke test running inside a real skirmish world.
local fighter, victim, startLocation, hitCount
local produced = false
local report = function(message)
    print("PIKEMAN TEST: " .. message)
    Media.DisplayMessage(message, "Pikeman test")
end
WorldLoaded = function()
    Trigger.AfterDelay(25, function()
        local owner = Player.GetPlayer("Multi0")
        local creeps = Player.GetPlayer("Creeps")
        fighter = Actor.Create("pikeman", true, { Owner = owner, Location = CPos.New(20, 23) })
        victim = Actor.Create("pike.target", true, { Owner = creeps, Location = CPos.New(25, 23) })
        fighter.Stance = "Defend"
        local airFighter = Actor.Create("pikeman", true, { Owner = owner, Location = CPos.New(40, 12) })
        local air = Actor.Create("tran", true, { Owner = creeps, CenterPosition = airFighter.CenterPosition + WVec.New(1024, 0, Actor.CruiseAltitude("tran")) })
        airFighter.Attack(air)
        Trigger.AfterDelay(60, function()
            if air.Health ~= air.MaxHealth then FatalError("Pikeman damaged airborne helicopter") end
            report("PASS: attack order dealt no damage to airborne helicopter.")
            air.Destroy()
            airFighter.Destroy()
        end)
        if not owner.Build({ "pikeman" }, function(units)
            if #units ~= 1 or units[1].Type ~= "pikeman" then FatalError("Unexpected production result") end
            produced = true
            report("PASS: trained a Pikeman through the normal barracks production queue.")
        end) then FatalError("Could not queue a Pikeman at the barracks") end
        startLocation = fighter.Location
        hitCount = 0
        Camera.Position = fighter.CenterPosition
        report("Hold-position range check: target is five tiles away.")
        Trigger.OnDamaged(victim, function(self, attacker, damage)
            if attacker ~= fighter then FatalError("Unexpected attacker in melee test") end
            local delta = fighter.CenterPosition - victim.CenterPosition
            local distance = math.sqrt(delta.X * delta.X + delta.Y * delta.Y)
            if distance > 1400 then FatalError("Pike damaged a target outside melee reach") end
            hitCount = hitCount + 1
            print("PIKEMAN HIT: damage=" .. damage .. " distance=" .. distance)
        end)
        Trigger.OnKilled(victim, function()
            if hitCount ~= 2 then FatalError("Expected two 2500-damage hits") end
            report("PASS: moved into melee range and killed target with two pike hits.")
        end)
        Trigger.AfterDelay(75, function()
            if victim.Health ~= victim.MaxHealth then FatalError("Pike dealt ranged damage") end
            if fighter.Location ~= startLocation then FatalError("Hold-position check moved") end
            report("PASS: no ranged damage. Now approaching for a melee attack.")
            fighter.Attack(victim)
        end)
        Trigger.AfterDelay(450, function()
            if not produced then FatalError("Barracks production did not complete") end
            if not victim.IsDead then FatalError("Melee attack failed to kill target") end
            report("PASS: skirmish smoke test complete. Train more Pikemen at the barracks.")
            -- Additional stationary targets for manual play.
            for i = 0, 3 do
                Actor.Create("pike.target", true, { Owner = creeps, Location = CPos.New(30, 20+i*2) })
            end
        end)
    end)
end
