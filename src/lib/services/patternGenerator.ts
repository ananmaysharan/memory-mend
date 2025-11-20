/**
 * Pattern generation service
 * Converts memories into stitch patterns
 *
 * NEW APPROACH (2025-11-15):
 * - Simplified pattern generation using short IDs
 * - Removed interactive editing features
 * - Patterns are now read-only representations of memory IDs
 * - Removed pattern statistics (no longer needed)
 */

import type { Memory, PatternData } from '$lib/types/mend';
import { hashMemory, idToBinary, binaryToGrid, calculateGridSize, ID_LENGTH } from '$lib/utils/hashUtils';

const DEFAULT_CELL_SIZE = 20; // 20px per cell for display

/**
 * Generate a pattern from a memory
 * The pattern is a visual representation of the memory's unique ID
 */
export async function generatePatternFromMemory(memory: Memory): Promise<PatternData> {
	// Get the short ID for the memory (e.g., "A1B2C3")
	const id = await hashMemory({ text: memory.text, image: memory.image });

	// Convert ID to binary (each character becomes 8 bits)
	const binary = idToBinary(id);

	// Calculate required grid size based on ID length
	const gridSize = calculateGridSize(ID_LENGTH);

	// Convert binary to grid (corners will be false, data cells based on binary)
	const grid = binaryToGrid(binary, gridSize);

	return {
		grid,
		id, // Store the ID for display/reference
		config: {
			gridSize,
			cellSize: DEFAULT_CELL_SIZE
		}
	};
}
