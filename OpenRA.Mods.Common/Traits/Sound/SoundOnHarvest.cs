#region Copyright & License Information
/*
 * Copyright (c) The OpenRA Developers and Contributors
 * This file is part of OpenRA, which is free software. It is made
 * available to you under the terms of the GNU General Public License
 * as published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version. For more
 * information, see COPYING.
 */
#endregion

using System.Collections.Immutable;
using OpenRA.Traits;

namespace OpenRA.Mods.Common.Traits.Sound
{
	[Desc("Plays an occasional positional sound on actual harvesting, never while walking or idle.")]
	public class SoundOnHarvestInfo : TraitInfo, Requires<HarvesterInfo>
	{
		public readonly ImmutableArray<string> SoundFiles = [];
		public readonly int Interval = 120;
		public override object Create(ActorInitializer init) { return new SoundOnHarvest(this); }
	}

	public class SoundOnHarvest : INotifyHarvestAction
	{
		readonly SoundOnHarvestInfo info;
		int nextSoundTick;

		public SoundOnHarvest(SoundOnHarvestInfo info) { this.info = info; }

		void INotifyHarvestAction.Harvested(Actor self, string resourceType)
		{
			if (self.World.WorldTick < nextSoundTick || self.World.FogObscures(self))
				return;

			nextSoundTick = self.World.WorldTick + info.Interval + (int)(self.ActorID % 25);
			Game.Sound.Play(SoundType.World, info.SoundFiles, self.World, self.CenterPosition, volumeModifier: 0.6f);
		}

		void INotifyHarvestAction.MovingToResources(Actor self, CPos targetCell) { }
		void INotifyHarvestAction.MovementCancelled(Actor self) { }
	}
}
