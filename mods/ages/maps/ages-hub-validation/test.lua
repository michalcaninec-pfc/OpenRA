-- Exercise the real Ages AI with paid hub production and automatic harvesting.
local bot, human, tick, firstHub, passed = nil, nil, 0, nil, false
local function check(ok, text) if not ok then FatalError(text) end end
WorldLoaded = function()
 Trigger.AfterDelay(25, function()
  bot = Player.GetPlayer('Multi1')
  human = Player.GetPlayer('Multi0')
  check(#bot.GetActorsByType('worker') == 3, 'Starting hub duplicated gatherers')
  check(#human.GetActorsByType('worker') == 3, 'Human starting hub duplicated gatherers')
  check(Actor.BuildTime('mhut') == 750, 'Hub build duration must be 750 ticks')
  check(Actor.Cost('mhut') == 600, 'Hub cost must be 600')
  Camera.Position = bot.GetActorsByType('mhut.start')[1].CenterPosition
  print('AGES HUB: PASS starting armies, price and duration')
 end)
end
Tick = function()
 tick = tick + 1
 if not bot or passed or tick % 25 ~= 0 then return end
 local hubs = #bot.GetActorsByType('mhut')
 local workers = #bot.GetActorsByType('worker')
 check(workers <= 3 + 3 * hubs, 'Workers trained outside hub construction')
 if hubs > 0 and not firstHub then
  check(tick >= 750, 'Hub completed too early')
  firstHub = tick
  print('AGES HUB: first paid hub placed at tick '..tick)
 end
 if tick % 250 == 0 then
  print('AGES HUB: tick='..tick..' hubs='..hubs..' workers='..workers..' cash='..bot.Cash)
 end
 if hubs == 2 and workers == 9 and tick > firstHub + 1600 then
  check(tick >= 1500, 'Two hubs bypassed the shared building queue')
  -- Initial $1800 minus two $600 hubs leaves at most $600 without mining.
  check(bot.Resources + bot.Cash > 600, 'No harvesting income after hub expansion')
  print('AGES HUB: PASS two paid hubs, exactly nine gatherers, harvesting income; tick='..tick)
  passed = true
 end
 check(tick < 7000, 'Hub AI validation timed out')
end
