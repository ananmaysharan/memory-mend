<script lang="ts">
	import type { PatternData } from '$lib/types/mend';
	import { extractDiagonalLines } from '$lib/utils/diagonalOptimizer';

	interface Props {
		pattern: PatternData;
		large?: boolean;
	}

	let { pattern, large = false }: Props = $props();

	// Calculate cell size based on display mode
	const baseCellSize = $derived(large ? 28 : pattern.config.cellSize);
	const cellSize = $derived(baseCellSize);
	const gridSize = $derived(pattern.config.gridSize);

	// Calculate optimized diagonal lines (no corner exclusion)
	const diagonalLines = $derived(extractDiagonalLines(pattern.grid));
</script>

<div class="pattern-container">
	<!-- Pattern Info -->
	<div class="mb-4 text-center">
		<p class="font-mono text-sm text-gray-600 m-0">
			<strong>Pattern ID:</strong>
			{pattern.id}
		</p>
	</div>

	<!-- Pattern Grid with Fiducials -->
	<div class="pattern-grid">
		<!-- Top row: TL fiducial, empty cells, TR fiducial -->
		<div class="flex">
			<!-- TL Fiducial: X -->
			<div class="cell" style="width: {cellSize}px; height: {cellSize}px;">
				<svg width={cellSize} height={cellSize} xmlns="http://www.w3.org/2000/svg">
					<line
						x1={cellSize * 0.1}
						y1={cellSize * 0.1}
						x2={cellSize * 0.9}
						y2={cellSize * 0.9}
						stroke="#000"
						stroke-width={cellSize * 0.12}
						stroke-linecap="butt"
					/>
					<line
						x1={cellSize * 0.9}
						y1={cellSize * 0.1}
						x2={cellSize * 0.1}
						y2={cellSize * 0.9}
						stroke="#000"
						stroke-width={cellSize * 0.12}
						stroke-linecap="butt"
					/>
				</svg>
			</div>
			{#each Array(gridSize) as _}
				<div class="cell" style="width: {cellSize}px; height: {cellSize}px;"></div>
			{/each}
			<!-- TR Fiducial: || -->
			<div class="cell" style="width: {cellSize}px; height: {cellSize}px;">
				<svg width={cellSize} height={cellSize} xmlns="http://www.w3.org/2000/svg">
					<line
						x1={cellSize * 0.35}
						y1={cellSize * 0.1}
						x2={cellSize * 0.35}
						y2={cellSize * 0.9}
						stroke="#000"
						stroke-width={cellSize * 0.12}
						stroke-linecap="butt"
					/>
					<line
						x1={cellSize * 0.65}
						y1={cellSize * 0.1}
						x2={cellSize * 0.65}
						y2={cellSize * 0.9}
						stroke="#000"
						stroke-width={cellSize * 0.12}
						stroke-linecap="butt"
					/>
				</svg>
			</div>
		</div>

		<!-- Middle rows: empty cell, 7x7 data grid, empty cell -->
		{#each pattern.grid as row, rowIndex}
			<div class="flex">
				<div class="cell" style="width: {cellSize}px; height: {cellSize}px;"></div>
				{#each row as cell, colIndex}
					<div class="cell" style="width: {cellSize}px; height: {cellSize}px;">
						<!-- Data cells - diagonal lines rendered in overlay -->
					</div>
				{/each}
				<div class="cell" style="width: {cellSize}px; height: {cellSize}px;"></div>
			</div>
		{/each}

		<!-- Bottom row: BL fiducial, empty cells, BR fiducial -->
		<div class="flex">
			<!-- BL Fiducial: O -->
			<div class="cell" style="width: {cellSize}px; height: {cellSize}px;">
				<svg width={cellSize} height={cellSize} xmlns="http://www.w3.org/2000/svg">
					<circle
						cx={cellSize / 2}
						cy={cellSize / 2}
						r={(cellSize - cellSize * 0.24) / 2}
						fill="none"
						stroke="#000"
						stroke-width={cellSize * 0.12}
					/>
				</svg>
			</div>
			{#each Array(gridSize) as _}
				<div class="cell" style="width: {cellSize}px; height: {cellSize}px;"></div>
			{/each}
			<!-- BR Fiducial: ■ -->
			<div class="cell" style="width: {cellSize}px; height: {cellSize}px;">
				<svg width={cellSize} height={cellSize} xmlns="http://www.w3.org/2000/svg">
					<rect
						x={cellSize * 0.1}
						y={cellSize * 0.1}
						width={cellSize * 0.8}
						height={cellSize * 0.8}
						fill="none"
						stroke="#000"
						stroke-width={cellSize * 0.12}
					/>
				</svg>
			</div>
		</div>

		<!-- Optimized diagonal lines overlay (offset by 1 cell) -->
		{#if diagonalLines.length > 0}
			<svg
				class="diagonal-overlay"
				width={(gridSize + 2) * cellSize}
				height={(gridSize + 2) * cellSize}
				style="position: absolute; top: 0; left: 0; pointer-events: none;"
				xmlns="http://www.w3.org/2000/svg"
			>
				{#each diagonalLines as line}
					{@const x1 = line.direction === 'nw-se'
						? (line.startCol + 1) * cellSize
						: (line.startCol + 2) * cellSize}
					{@const y1 = (line.startRow + 1) * cellSize}
					{@const x2 = line.direction === 'nw-se'
						? (line.endCol + 2) * cellSize
						: (line.endCol + 1) * cellSize}
					{@const y2 = (line.endRow + 2) * cellSize}

					<line
						x1={x1}
						y1={y1}
						x2={x2}
						y2={y2}
						stroke="#000"
						stroke-width={cellSize * 0.12}
						stroke-linecap="butt"
					/>
				{/each}
			</svg>
		{/if}
	</div>
</div>

<style>
	.pattern-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 100%;
	}

	.pattern-grid {
		display: inline-flex;
		flex-direction: column;
		position: relative; /* Enable absolute positioning for diagonal overlay */
	}

	.cell {
		border: 1px solid #fff;
		box-sizing: border-box;
	}

	/* Responsive sizing for smaller screens */
	@media (max-width: 640px) {
		.pattern-grid {
			transform: scale(0.75);
			transform-origin: top center;
		}
	}
</style>
