/**
 * G-code generation configuration and types
 */

/**
 * Stitch configuration for G-code generation
 */
export interface StitchConfig {
	stitchSpacing: number; // Distance between stitches in mm
	hoopOffsetX: number; // X offset from hoop origin in mm
	hoopOffsetY: number; // Y offset from hoop origin in mm
	stitchSpeed: number; // Stitching speed (units/min)
	travelSpeed: number; // Travel speed between stitches (units/min)
	patternScale: number; // Scale factor for pattern (1.0 = original size)
}

/**
 * G-code command types
 */
export type GCodeCommand = {
	command: string; // e.g., "G00", "G01"
	params: Record<string, number | string>; // e.g., { X: 10, Y: 20, F: 500 }
	comment?: string;
};

/**
 * Default stitch configuration
 */
export const DEFAULT_STITCH_CONFIG: StitchConfig = {
	stitchSpacing: 2.5, // 2.5mm between stitches
	hoopOffsetX: 0,
	hoopOffsetY: 0,
	stitchSpeed: 800, // mm/min
	travelSpeed: 3000, // mm/min
	patternScale: 1.0
};
