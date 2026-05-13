// Map a (gx, gy) grid coordinate from the priority-zone CSV to screen pixels
// inside the 1080×1080 frame. Pretends the city is a tilted square aligned
// with the BarcelonaMap primitive's Eixample grid rotation.
//
// The transformation is purely visual — these are not real coordinates.

import { gridBounds } from "../data/priorityZones";

const GRID_ROTATION_DEG = -36;

export type ScreenPoint = { x: number; y: number };

const gridCenter = {
  cx: (gridBounds.minX + gridBounds.maxX) / 2,
  cy: (gridBounds.minY + gridBounds.maxY) / 2,
};

const screenCenter = { x: 540, y: 540 };

// Cell pitch in screen pixels — calibrated so 15 zones spread visibly.
const CELL_PITCH = 30;

export const gridToScreen = (gx: number, gy: number): ScreenPoint => {
  // Translate to grid-centered local coordinates
  const localX = (gx - gridCenter.cx) * CELL_PITCH;
  const localY = (gy - gridCenter.cy) * CELL_PITCH;

  // Apply Eixample rotation
  const rad = (GRID_ROTATION_DEG * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  const rotX = localX * cos - localY * sin;
  const rotY = localX * sin + localY * cos;

  return {
    x: screenCenter.x + rotX,
    y: screenCenter.y + rotY,
  };
};
