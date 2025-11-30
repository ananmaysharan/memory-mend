/**
 * SVG generation service for embroidery patterns
 * Generates downloadable SVG files with optimized diagonal lines
 */

import type { PatternData } from '$lib/types/mend';
import { extractDiagonalLines } from '$lib/utils/diagonalOptimizer';

/**
 * Generate SVG string from pattern data
 * @param pattern - Pattern data to convert
 * @param cellSize - Size of each cell in pixels (default: 20)
 * @returns SVG string
 */
export function generateSVG(pattern: PatternData, cellSize: number = 20): string {
	const gridSize = pattern.config.gridSize;
	const width = (gridSize + 2) * cellSize; // +2 for fiducial border
	const height = (gridSize + 2) * cellSize;

	const diagonalLines = extractDiagonalLines(pattern.grid);

	let svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
  <title>Memory Mend Pattern - ${pattern.id}</title>
  <desc>Embroidery pattern for memory ID: ${pattern.id}</desc>

  <!-- Fiducial markers -->
  <g id="fiducials" stroke="#000" stroke-width="${cellSize * 0.12}" stroke-linecap="butt" fill="none">
`;

	// Top-left fiducial: X
	svg += `    <!-- TL: X -->\n`;
	svg += `    <line x1="${cellSize * 0.1}" y1="${cellSize * 0.1}" x2="${cellSize * 0.9}" y2="${cellSize * 0.9}" />\n`;
	svg += `    <line x1="${cellSize * 0.9}" y1="${cellSize * 0.1}" x2="${cellSize * 0.1}" y2="${cellSize * 0.9}" />\n`;

	// Top-right fiducial: ||
	const trX = (gridSize + 1) * cellSize;
	svg += `    <!-- TR: || -->\n`;
	svg += `    <line x1="${trX + cellSize * 0.35}" y1="${cellSize * 0.1}" x2="${trX + cellSize * 0.35}" y2="${cellSize * 0.9}" />\n`;
	svg += `    <line x1="${trX + cellSize * 0.65}" y1="${cellSize * 0.1}" x2="${trX + cellSize * 0.65}" y2="${cellSize * 0.9}" />\n`;

	// Bottom-left fiducial: O
	const blY = (gridSize + 1) * cellSize;
	svg += `    <!-- BL: O -->\n`;
	svg += `    <circle cx="${cellSize / 2}" cy="${blY + cellSize / 2}" r="${(cellSize - cellSize * 0.24) / 2}" />\n`;

	// Bottom-right fiducial: ■
	const brX = (gridSize + 1) * cellSize;
	const brY = (gridSize + 1) * cellSize;
	svg += `    <!-- BR: ■ -->\n`;
	svg += `    <rect x="${brX + cellSize * 0.1}" y="${brY + cellSize * 0.1}" width="${cellSize * 0.8}" height="${cellSize * 0.8}" />\n`;

	svg += `  </g>\n\n`;
	svg += `  <!-- Optimized diagonal stitch lines -->\n`;
	svg += `  <g id="stitches" stroke="#000" stroke-width="${cellSize * 0.12}" stroke-linecap="butt">\n`;

	// Add diagonal lines (offset by 1 cell for fiducial border)
	for (const line of diagonalLines) {
		const x1 = line.direction === 'nw-se'
			? (line.startCol + 1) * cellSize
			: (line.startCol + 2) * cellSize;
		const y1 = (line.startRow + 1) * cellSize;
		const x2 = line.direction === 'nw-se'
			? (line.endCol + 2) * cellSize
			: (line.endCol + 1) * cellSize;
		const y2 = (line.endRow + 2) * cellSize;

		svg += `    <line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" />\n`;
	}

	svg += `  </g>\n</svg>`;
	return svg;
}

/**
 * Download SVG as a file
 * @param svg - SVG string to download
 * @param filename - Filename (default: pattern.svg)
 */
export function downloadSVG(svg: string, filename: string = 'pattern.svg'): void {
	const blob = new Blob([svg], { type: 'image/svg+xml' });
	const url = URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = filename;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
	URL.revokeObjectURL(url);
}

/**
 * Generate and download SVG for a pattern
 * @param pattern - Pattern data to convert
 * @param cellSize - Size of each cell in pixels (default: 20)
 */
export function downloadPatternSVG(pattern: PatternData, cellSize: number = 20): void {
	const svg = generateSVG(pattern, cellSize);
	const filename = `memory-mend-${pattern.id}.svg`;
	downloadSVG(svg, filename);
}
