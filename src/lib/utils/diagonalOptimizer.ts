/**
 * Diagonal line optimization for embroidery efficiency
 * Converts individual X-mark stitches into continuous diagonal lines
 */

export interface DiagonalLine {
	startRow: number;
	startCol: number;
	endRow: number;
	endCol: number;
	direction: 'nw-se' | 'ne-sw'; // NW-SE (slope=1) or NE-SW (slope=-1)
}

/**
 * Extract continuous diagonal lines from a boolean grid
 * @param grid - 2D boolean array where true = stitch required
 * @param skipCorners - Optional set of corner coordinates to skip (e.g., "0,0", "0,6")
 */
export function extractDiagonalLines(
	grid: boolean[][],
	skipCorners: Set<string> = new Set()
): DiagonalLine[] {
	const gridSize = grid.length;
	const lines: DiagonalLine[] = [];

	const visitedNWSE = new Set<string>();
	const visitedNESW = new Set<string>();

	const isValidStitch = (row: number, col: number): boolean => {
		if (row < 0 || row >= gridSize || col < 0 || col >= gridSize) return false;
		if (skipCorners?.has(`${row},${col}`)) return false;
		return grid[row][col];
	};

	const markVisited = (row: number, col: number, direction: 'nw-se' | 'ne-sw'): void => {
		const key = `${row},${col}`;
		if (direction === 'nw-se') {
			visitedNWSE.add(key);
		} else {
			visitedNESW.add(key);
		}
	};

	const isVisited = (row: number, col: number, direction: 'nw-se' | 'ne-sw'): boolean => {
		const key = `${row},${col}`;
		return direction === 'nw-se' ? visitedNWSE.has(key) : visitedNESW.has(key);
	};

	// Trace NW-SE diagonals (slope = 1, direction: ↘)
	for (let row = 0; row < gridSize; row++) {
		for (let col = 0; col < gridSize; col++) {
			if (!isValidStitch(row, col) || isVisited(row, col, 'nw-se')) continue;

			const startRow = row;
			const startCol = col;
			let endRow = row;
			let endCol = col;

			markVisited(row, col, 'nw-se');
			while (isValidStitch(endRow + 1, endCol + 1)) {
				endRow++;
				endCol++;
				markVisited(endRow, endCol, 'nw-se');
			}

			lines.push({ startRow, startCol, endRow, endCol, direction: 'nw-se' });
		}
	}

	// Trace NE-SW diagonals (slope = -1, direction: ↙)
	for (let row = 0; row < gridSize; row++) {
		for (let col = 0; col < gridSize; col++) {
			if (!isValidStitch(row, col) || isVisited(row, col, 'ne-sw')) continue;

			const startRow = row;
			const startCol = col;
			let endRow = row;
			let endCol = col;

			markVisited(row, col, 'ne-sw');
			while (isValidStitch(endRow + 1, endCol - 1)) {
				endRow++;
				endCol--;
				markVisited(endRow, endCol, 'ne-sw');
			}

			lines.push({ startRow, startCol, endRow, endCol, direction: 'ne-sw' });
		}
	}

	return lines;
}
