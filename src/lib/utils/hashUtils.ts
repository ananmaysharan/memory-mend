/**
 * Utilities for hashing memories and converting to binary patterns
 *
 * NEW APPROACH (2025-11-15):
 * - Simple hash function generates short, configurable-length IDs (default 6 digits)
 * - ID is base36 encoded (0-9, A-Z)
 * - Each character of ID is converted to 8-bit binary
 * - Binary is mapped to grid with corner markers
 */

/**
 * Configuration for ID generation
 * Change ID_LENGTH to adjust grid size (more characters = larger grid needed)
 */
export const ID_LENGTH = 6; // Each character = 8 bits = needs 6*8 = 48 bits total

/**
 * Simple hash function to generate short IDs
 * Based on the approach from the reference implementation
 */
function simpleHash(message: string): number {
	let hash = 0;
	for (let i = 0; i < message.length; i++) {
		const char = message.charCodeAt(i);
		hash = ((hash << 5) - hash) + char;
		hash = hash & hash; // Convert to 32bit integer
	}
	return Math.abs(hash);
}

/**
 * Hash a memory (text or image) into a unique short ID
 * Returns a base36 string (0-9, A-Z) of length ID_LENGTH
 */
export async function hashMemory(memory: { text?: string; image?: string }): Promise<string> {
	let hashInput = '';

	if (memory.text) {
		hashInput = memory.text;
	}

	if (memory.image) {
		// For images, use a substring of the base64 data
		hashInput += memory.image.substring(0, 1000);
	}

	if (!hashInput) {
		// Fallback for empty input
		hashInput = Date.now().toString();
	}

	const hash = simpleHash(hashInput);
	// Convert to base36 (0-9, A-Z) and take first ID_LENGTH characters, pad if needed
	return hash.toString(36).toUpperCase().substring(0, ID_LENGTH).padEnd(ID_LENGTH, '0');
}

/**
 * Convert an ID string to binary representation
 * Each character is converted to 8-bit binary
 */
export function idToBinary(id: string): string {
	return id.split('').map(char => {
		return char.charCodeAt(0).toString(2).padStart(8, '0');
	}).join('');
}

/**
 * Calculate required grid size for a given ID length
 * Grid needs 4 corner cells + data cells for binary representation
 * Each ID character = 8 bits
 *
 * Formula: gridSize^2 = 4 (corners) + (ID_LENGTH * 8) (data bits)
 * So: gridSize = ceil(sqrt(4 + ID_LENGTH * 8))
 */
export function calculateGridSize(idLength: number = ID_LENGTH): number {
	const dataBits = idLength * 8;
	const totalCells = 4 + dataBits; // 4 corner markers + data cells
	return Math.ceil(Math.sqrt(totalCells));
}

/**
 * Convert binary string to a 2D boolean grid
 * Corner cells (0,0), (0,gridSize-1), (gridSize-1,0), (gridSize-1,gridSize-1) are reserved for markers
 *
 * @param binary - Binary string from idToBinary()
 * @param gridSize - Size of the square grid
 */
export function binaryToGrid(binary: string, gridSize: number): boolean[][] {
	const grid: boolean[][] = [];
	let bitIndex = 0;

	for (let row = 0; row < gridSize; row++) {
		const rowArray: boolean[] = [];
		for (let col = 0; col < gridSize; col++) {
			// Check if this is a corner cell
			const isCorner = (row === 0 && col === 0) ||
			                 (row === 0 && col === gridSize - 1) ||
			                 (row === gridSize - 1 && col === 0) ||
			                 (row === gridSize - 1 && col === gridSize - 1);

			if (isCorner) {
				// Corner cells are always false (handled separately in rendering)
				rowArray.push(false);
			} else {
				// Data cells: set based on binary string
				rowArray.push(bitIndex < binary.length && binary[bitIndex] === '1');
				bitIndex++;
			}
		}
		grid.push(rowArray);
	}

	return grid;
}

/**
 * Convert a 2D boolean grid back to binary string
 * Skips corner cells
 */
export function gridToBinary(grid: boolean[][]): string {
	const gridSize = grid.length;
	let binary = '';

	for (let row = 0; row < gridSize; row++) {
		for (let col = 0; col < grid[row].length; col++) {
			// Skip corner cells
			const isCorner = (row === 0 && col === 0) ||
			                 (row === 0 && col === gridSize - 1) ||
			                 (row === gridSize - 1 && col === 0) ||
			                 (row === gridSize - 1 && col === gridSize - 1);

			if (!isCorner) {
				binary += grid[row][col] ? '1' : '0';
			}
		}
	}

	return binary;
}

/**
 * Get corner marker type for a given corner position
 */
export function getCornerMarker(row: number, col: number, gridSize: number): 'TL' | 'TR' | 'BL' | 'BR' | null {
	if (row === 0 && col === 0) return 'TL'; // Top-left: X pattern
	if (row === 0 && col === gridSize - 1) return 'TR'; // Top-right: || pattern
	if (row === gridSize - 1 && col === 0) return 'BL'; // Bottom-left: O pattern
	if (row === gridSize - 1 && col === gridSize - 1) return 'BR'; // Bottom-right: solid square
	return null;
}
