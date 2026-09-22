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

using System;
using System.Numerics;
using OpenRA.Graphics;
using OpenRA.Primitives;

namespace OpenRA.Mods.Common.Graphics
{
	public class RangeCircleAnnotationRenderable : IRenderable, IFinalizedRenderable
	{
		const int RangeCircleSegments = 32;
		static readonly Int32Matrix4x4[] RangeCircleStartRotations = Exts.MakeArray(RangeCircleSegments, i => WRot.FromFacing(8 * i).AsMatrix());
		static readonly Int32Matrix4x4[] RangeCircleEndRotations = Exts.MakeArray(RangeCircleSegments, i => WRot.FromFacing(8 * i + 6).AsMatrix());
		readonly WDist radius;
		readonly Color color;
		readonly float width;
		readonly Color borderColor;
		readonly float borderWidth;
		readonly bool respectFog;

		public RangeCircleAnnotationRenderable(WPos centerPosition, WDist radius, int zOffset, Color color, float width, Color borderColor, float borderWidth)
			: this(centerPosition, radius, zOffset, color, width, borderColor, borderWidth, false) { }

		public RangeCircleAnnotationRenderable(WPos centerPosition, WDist radius, int zOffset, Color color, float width, Color borderColor, float borderWidth, bool respectFog)
		{
			Pos = centerPosition;
			this.radius = radius;
			ZOffset = zOffset;
			this.color = color;
			this.width = width;
			this.borderColor = borderColor;
			this.borderWidth = borderWidth;
			this.respectFog = respectFog;
		}

		public WPos Pos { get; }
		public int ZOffset { get; }
		public bool IsDecoration => true;

		public IRenderable WithZOffset(int newOffset) { return new RangeCircleAnnotationRenderable(Pos, radius, newOffset, color, width, borderColor, borderWidth, respectFog); }
		public IRenderable OffsetBy(in WVec vec) { return new RangeCircleAnnotationRenderable(Pos + vec, radius, ZOffset, color, width, borderColor, borderWidth, respectFog); }
		public IRenderable AsDecoration() { return this; }

		public IFinalizedRenderable PrepareRender(WorldRenderer wr) { return this; }
		public void Render(WorldRenderer wr)
		{
			DrawRangeCircle(wr, Pos, radius, width, color, borderWidth, borderColor, respectFog);
		}

		public static void DrawRangeCircle(WorldRenderer wr, WPos centerPosition, WDist radius,
			float width, Color color, float borderWidth, Color borderColor)
		{
			DrawRangeCircle(wr, centerPosition, radius, width, color, borderWidth, borderColor, false);
		}

		public static void DrawRangeCircle(WorldRenderer wr, WPos centerPosition, WDist radius,
			float width, Color color, float borderWidth, Color borderColor, bool respectFog)
		{
			var cr = Game.Renderer.RgbaColorRenderer;
			var offset = new WVec(radius.Length, 0, 0);
			for (var i = 0; i < RangeCircleSegments; i++)
			{
				var start = centerPosition + offset.Rotate(ref RangeCircleStartRotations[i]);
				var end = centerPosition + offset.Rotate(ref RangeCircleEndRotations[i]);
				// Small world-space sections avoid exposing an entire dash across a fog boundary.
				var steps = respectFog ? Math.Max(1, ((end - start).Length + 127) / 128) : 1;
				for (var step = 0; step < steps; step++)
				{
					var from = WPos.Lerp(start, end, step, steps);
					var to = WPos.Lerp(start, end, step + 1, steps);
					var midpoint = WPos.Lerp(from, to, 1, 2);
					if (respectFog && (wr.World.FogObscures(from) || wr.World.ShroudObscures(from) ||
						wr.World.FogObscures(to) || wr.World.ShroudObscures(to) ||
						wr.World.FogObscures(midpoint) || wr.World.ShroudObscures(midpoint)))
						continue;

					var a = wr.Viewport.WorldToViewPx(wr.ScreenPosition(from).AsVector3()).ToVector3();
					var b = wr.Viewport.WorldToViewPx(wr.ScreenPosition(to).AsVector3()).ToVector3();
					if (borderWidth > 0)
						cr.DrawLine(a, b, borderWidth, borderColor);

					if (width > 0)
						cr.DrawLine(a, b, width, color);
				}
			}
		}

		public void RenderDebugGeometry(WorldRenderer wr) { }
		public Rectangle ScreenBounds(WorldRenderer wr) { return Rectangle.Empty; }
	}
}
