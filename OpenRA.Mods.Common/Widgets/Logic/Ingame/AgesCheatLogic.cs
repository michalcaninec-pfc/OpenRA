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

using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;
using OpenRA.Widgets;

namespace OpenRA.Mods.Common.Widgets.Logic
{
	public class AgesCheatLogic : ChromeLogic
	{
		[ObjectCreator.UseCtor]
		public AgesCheatLogic(Widget widget, World world)
		{
			var player = world.LocalPlayer.PlayerActor;
			var developer = player.Trait<DeveloperMode>();
			var reveal = widget.Get<ButtonWidget>("AGES_REVEAL");
			reveal.IsDisabled = () => !developer.Enabled || world.IsGameOver;
			reveal.IsHighlighted = () => developer.DisableShroud;
			reveal.OnClick = () => world.IssueOrder(new Order(DeveloperMode.Orders.Visibility, player, false));

			var cash = widget.Get<ButtonWidget>("AGES_CASH");
			cash.IsDisabled = () => !developer.Enabled || world.IsGameOver;
			cash.OnClick = () => world.IssueOrder(new Order(DeveloperMode.Orders.GiveCash, player, false) { ExtraData = 5000 });
		}
	}
}
