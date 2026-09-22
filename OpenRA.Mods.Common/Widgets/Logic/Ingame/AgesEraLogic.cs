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
	public class AgesEraLogic : ChromeLogic
	{
		[FluentReference]
		const string Medieval = "ages-era-medieval";
		[FluentReference]
		const string Gunpowder = "ages-era-gunpowder";
		[FluentReference]
		const string Industrial = "ages-era-industrial";

		[ObjectCreator.UseCtor]
		public AgesEraLogic(Widget widget, World world)
		{
			var tech = world.LocalPlayer.PlayerActor.Trait<TechTree>();
			var medieval = FluentProvider.GetMessage(Medieval);
			var gunpowder = FluentProvider.GetMessage(Gunpowder);
			var industrial = FluentProvider.GetMessage(Industrial);
			((LabelWidget)widget).GetText = () => tech.HasPrerequisites(["modern.age"]) ? industrial :
				tech.HasPrerequisites(["gunpowder.age"]) ? gunpowder : medieval;
		}
	}
}
