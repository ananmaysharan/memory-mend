/**
 * G-code generation service
 * Converts stitch patterns to embroidery machine G-code
 */

import type { PatternData } from '$lib/types/mend';
import type { StitchConfig } from '$lib/types/gcode';
import { DEFAULT_STITCH_CONFIG } from '$lib/types/gcode';

/**
 * Generate G-code from a pattern
 */
export function generateGCode(pattern: PatternData, config: StitchConfig = DEFAULT_STITCH_CONFIG): string {
	const lines: string[] = [];

	// Header
	lines.push('; Memory Mend - Auto-generated G-code');
	lines.push(`; Generated: ${new Date().toISOString()}`);
	lines.push(`; Pattern size: ${pattern.grid.length}x${pattern.grid[0].length}`);
	lines.push('');

	// Initialization
	lines.push('; Initialize');
	lines.push('G21 ; Set units to millimeters');
	lines.push('G90 ; Absolute positioning');
	lines.push('M3 ; Needle down (prepare to stitch)');
	lines.push('');

	// Move to start position
	lines.push('; Move to start position');
	lines.push(`G0 X${config.hoopOffsetX} Y${config.hoopOffsetY} F${config.travelSpeed}`);
	lines.push('');

	// Generate stitches
	lines.push('; Begin stitching pattern');
	let stitchCount = 0;

	for (let row = 0; row < pattern.grid.length; row++) {
		for (let col = 0; col < pattern.grid[row].length; col++) {
			if (pattern.grid[row][col]) {
				// Calculate position
				const x = config.hoopOffsetX + col * config.stitchSpacing * config.patternScale;
				const y = config.hoopOffsetY + row * config.stitchSpacing * config.patternScale;

				// Move and stitch
				lines.push(`G1 X${x.toFixed(2)} Y${y.toFixed(2)} F${config.stitchSpeed} ; Stitch ${++stitchCount}`);
			}
		}
	}

	lines.push('');
	lines.push(`; Total stitches: ${stitchCount}`);

	// End sequence
	lines.push('');
	lines.push('; End sequence');
	lines.push('M5 ; Needle up');
	lines.push(`G0 X${config.hoopOffsetX} Y${config.hoopOffsetY} F${config.travelSpeed} ; Return to origin`);
	lines.push('M2 ; Program end');
	lines.push('');

	return lines.join('\n');
}

/**
 * Validate G-code (basic validation)
 */
export function validateGCode(gcode: string): { valid: boolean; errors: string[] } {
	const errors: string[] = [];

	if (!gcode || gcode.trim().length === 0) {
		errors.push('G-code is empty');
	}

	// Check for required commands
	const requiredCommands = ['G21', 'G90', 'M2'];
	for (const cmd of requiredCommands) {
		if (!gcode.includes(cmd)) {
			errors.push(`Missing required command: ${cmd}`);
		}
	}

	return {
		valid: errors.length === 0,
		errors
	};
}

/**
 * Estimate execution time for G-code (rough approximation)
 */
export function estimateExecutionTime(
	gcode: string,
	config: StitchConfig = DEFAULT_STITCH_CONFIG
): number {
	const lines = gcode.split('\n');
	let totalTime = 0; // in seconds

	for (const line of lines) {
		const trimmed = line.trim();
		if (trimmed.startsWith('G1')) {
			// Stitching move - estimate based on stitch speed
			totalTime += 60 / config.stitchSpeed; // Rough approximation
		} else if (trimmed.startsWith('G0')) {
			// Rapid move - estimate based on travel speed
			totalTime += 60 / config.travelSpeed;
		}
	}

	return Math.ceil(totalTime);
}

/**
 * Get G-code statistics
 */
export function getGCodeStats(gcode: string): {
	lineCount: number;
	stitchCount: number;
	moveCount: number;
	commentCount: number;
} {
	const lines = gcode.split('\n');
	let stitchCount = 0;
	let moveCount = 0;
	let commentCount = 0;

	for (const line of lines) {
		const trimmed = line.trim();
		if (trimmed.startsWith(';')) {
			commentCount++;
		} else if (trimmed.startsWith('G1')) {
			stitchCount++;
		} else if (trimmed.startsWith('G0')) {
			moveCount++;
		}
	}

	return {
		lineCount: lines.length,
		stitchCount,
		moveCount,
		commentCount
	};
}

/**
 * Download G-code as a file
 */
export function downloadGCode(gcode: string, filename: string = 'pattern.gcode'): void {
	const blob = new Blob([gcode], { type: 'text/plain' });
	const url = URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = filename;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
	URL.revokeObjectURL(url);
}
