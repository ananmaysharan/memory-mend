/**
 * Pattern migration utilities
 * Handles migrating old patterns to new 7x7 6-character ID patterns
 * Previous formats: 16x16 (original), 8x8 (Nov 2025)
 */

import type { Mend, PatternData } from '$lib/types/mend';
import { generatePatternFromMemory } from '$lib/services/patternGenerator';

/**
 * Check if a pattern needs migration (old format)
 * Old patterns: 16x16 grid (original) or 8x8 grid (Nov 2025), no 'id' field
 * New patterns: 7x7 grid with 'id' field
 */
export function needsMigration(pattern: PatternData): boolean {
	// Check if pattern has 'id' field - new patterns have this
	if (!pattern.id) {
		return true;
	}

	// Check if grid size is wrong (old patterns were 16x16 or 8x8)
	if (pattern.grid.length !== pattern.config.gridSize) {
		return true;
	}

	// Check if grid size is old size (16x16 or 8x8 instead of 7x7)
	if (pattern.config.gridSize === 16 || pattern.config.gridSize === 8) {
		return true;
	}

	return false;
}

/**
 * Migrate a mend from old pattern format to new format
 * Regenerates the pattern from the memory using new algorithm
 */
export async function migrateMend(mend: Mend): Promise<Mend> {
	// Regenerate pattern from memory using new algorithm
	const newPattern = await generatePatternFromMemory(mend.memory);

	return {
		...mend,
		pattern: newPattern,
		updatedAt: Date.now()
	};
}

/**
 * Migrate all mends that need migration
 */
export async function migrateAllMends(mends: Mend[]): Promise<Mend[]> {
	const migratedMends: Mend[] = [];

	for (const mend of mends) {
		if (needsMigration(mend.pattern)) {
			const migrated = await migrateMend(mend);
			migratedMends.push(migrated);
		} else {
			migratedMends.push(mend);
		}
	}

	return migratedMends;
}
