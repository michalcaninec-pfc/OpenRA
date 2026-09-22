#region Copyright & License Information
/* Copyright (c) The OpenRA Developers and Contributors
 * This file is part of OpenRA, licensed under GPL version 3 or later. */
#endregion

using System;
using System.Linq;
using System.Text.Json;
using OpenRA.Graphics;
using OpenRA.Traits;

namespace OpenRA.Mods.Common.Traits
{
	[Desc("Optional local diagnostic snapshots for Ages skirmish launches.")]
	[TraitLocation(SystemActors.World)]
	public class AgesMatchTelemetryInfo : TraitInfo
	{
		public readonly int Interval = 250;
		public override object Create(ActorInitializer init) { return new AgesMatchTelemetry(this); }
	}

	public class AgesMatchTelemetry : IWorldLoaded, ITick, IGameOver, INotifyActorDisposing
	{
		readonly AgesMatchTelemetryInfo info;
		World world;
		string match;
		bool enabled;
		bool ended;

		public AgesMatchTelemetry(AgesMatchTelemetryInfo info) { this.info = info; }

		public void Record(string kind, object data)
		{
			if (!enabled)
				return;

			try
			{
				Console.WriteLine("AGES_TELEMETRY " + JsonSerializer.Serialize(new
				{
					schema = 1, match, tick = world.WorldTick, kind, data
				}));
			}
			catch (Exception)
			{
				// Diagnostics must never interrupt a match, including on broken output pipes.
				enabled = false;
			}
		}

		void IWorldLoaded.WorldLoaded(World w, WorldRenderer wr)
		{
			world = w;
			enabled = Environment.GetEnvironmentVariable("AGES_TELEMETRY") == "1" &&
				w.Type == WorldType.Regular && !w.IsReplay;
			if (!enabled)
				return;

			match = Guid.NewGuid().ToString("N");
			Record("match_start", new
			{
				map = w.Map.Title, map_uid = w.Map.Uid, timestep_ms = w.Timestep,
				utc = DateTime.UtcNow.ToString("O"), snapshot_ticks = info.Interval,
				players = w.Players.Where(p => !p.NonCombatant).Select(p => new
				{
					id = p.InternalName, name = p.ResolvedPlayerName, bot = p.BotType,
					faction = p.Faction.InternalName, team = w.LobbyInfo.ClientWithIndex(p.ClientIndex)?.Team
				}).ToArray()
			});
			w.ActorAdded += ActorAdded;
			w.ActorRemoved += ActorRemoved;
		}

		static object ActorData(Actor a)
		{
			var health = a.TraitOrDefault<Health>();
			return new
			{
				id = a.ActorID, type = a.Info.Name, owner = a.Owner.InternalName,
				cell = a.OccupiesSpace == null ? null : new[] { a.Location.X, a.Location.Y },
				hp = health?.HP, max_hp = health?.MaxHP, dead = a.IsDead, idle = a.IsIdle,
				mobile = a.Info.HasTraitInfo<MobileInfo>(),
				combat = a.TraitsImplementing<AttackBase>().Any(),
				activity = a.CurrentActivity?.DebugLabelComponents().ToArray() ?? [],
				targets = a.CurrentActivity?.GetTargets(a).Where(t => t.Type != TargetType.Invalid)
					.Select(t => new[] { t.CenterPosition.X, t.CenterPosition.Y }).Take(4).ToArray() ?? []
			};
		}

		static bool Relevant(Actor a) => !a.Owner.NonCombatant || a.Info.Name == "village.center";
		void RecordActor(string kind, Actor a)
		{
			if (!enabled || !Relevant(a))
				return;

			try { Record(kind, ActorData(a)); }
			catch (Exception e) { Record("telemetry_error", new { message = e.Message }); enabled = false; }
		}

		void ActorAdded(Actor a) { RecordActor("actor_added", a); }
		void ActorRemoved(Actor a) { RecordActor("actor_removed", a); }

		void Snapshot()
		{
			var actors = world.Actors.Where(a => a.IsInWorld && !a.IsDead && Relevant(a)).ToArray();
			Record("snapshot", new
			{
				players = world.Players.Where(p => !p.NonCombatant).Select(p =>
				{
					var r = p.PlayerActor.TraitOrDefault<PlayerResources>();
					var stats = p.PlayerActor.TraitOrDefault<PlayerStatistics>();
					var dev = p.PlayerActor.TraitOrDefault<DeveloperMode>();
					return new
					{
						id = p.InternalName, outcome = p.WinState.ToString(), cash = r?.Cash,
						resources = r?.Resources, capacity = r?.ResourceCapacity, earned = r?.Earned, spent = r?.Spent,
						army_value = stats?.ArmyValue, killed = stats?.UnitsKilled, lost = stats?.UnitsDead,
						buildings_lost = stats?.BuildingsDead, loss_value = stats?.DeathsCost,
						cheats = new { enabled = dev?.Enabled, reveal = dev?.DisableShroud, fast_build = dev?.FastBuild, all_tech = dev?.AllTech },
						counts = actors.Where(a => a.Owner == p).GroupBy(a => a.Info.Name).ToDictionary(g => g.Key, g => g.Count()),
						queues = actors.Where(a => a.Owner == p).SelectMany(a => a.TraitsImplementing<ProductionQueue>())
							.Select(q => new { type = q.Info.Type, enabled = q.Enabled, items = q.AllQueued().Select(i => new
							{ type = i.Item, remaining = i.RemainingTime, cost_left = i.RemainingCost, paused = i.Paused, done = i.Done }).ToArray() }).ToArray()
					};
				}).ToArray(),
				actors = actors.Select(ActorData).ToArray()
			});
		}

		void ITick.Tick(Actor self)
		{
			if (!enabled || ended || (world.WorldTick != 1 && world.WorldTick % Math.Max(1, info.Interval) != 0))
				return;

			try { Snapshot(); }
			catch (Exception e) { Record("telemetry_error", new { message = e.Message }); enabled = false; }
		}

		void Finish(string reason)
		{
			if (!enabled || ended)
				return;

			try { Snapshot(); }
			catch (Exception e) { Record("telemetry_error", new { message = e.Message }); }
			Record("match_end", new { reason, outcomes = world.Players.Where(p => !p.NonCombatant)
				.Select(p => new { player = p.InternalName, outcome = p.WinState.ToString() }).ToArray() });
			ended = true;
		}

		void IGameOver.GameOver(World w) { Finish("game_over"); }
		void INotifyActorDisposing.Disposing(Actor self)
		{
			Finish("world_closed");
			if (world != null)
			{
				world.ActorAdded -= ActorAdded;
				world.ActorRemoved -= ActorRemoved;
			}
		}
	}

	public class AgesTelemetryOrdersInfo : TraitInfo
	{
		public override object Create(ActorInitializer init) { return new AgesTelemetryOrders(); }
	}

	public class AgesTelemetryOrders : IResolveOrder
	{
		void IResolveOrder.ResolveOrder(Actor self, Order order)
		{
			if (order.OrderString.StartsWith("Dev", StringComparison.Ordinal))
				self.World.WorldActor.TraitOrDefault<AgesMatchTelemetry>()?.Record("cheat_order",
					new { player = self.Owner.InternalName, order = order.OrderString, amount = order.ExtraData });
		}
	}
}
