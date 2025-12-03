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
	const gap = $derived(cellSize * 0.15);

	// Calculate optimized diagonal lines (no corner exclusion)
	const diagonalLines = $derived(extractDiagonalLines(pattern.grid));
</script>

<div class="flex flex-col items-center w-full">
	<!-- Pattern Grid with Fiducials -->
	<div class="inline-flex flex-col relative">
		<!-- Top row: TL fiducial, empty cells, TR fiducial -->
		<div class="flex">
			<!-- TL Fiducial: X -->
			<div
				class="border border-white box-border"
				style="width: {cellSize}px; height: {cellSize}px;"
			>
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
				<div
					class="border border-white box-border"
					style="width: {cellSize}px; height: {cellSize}px;"
				></div>
			{/each}
			<!-- TR Fiducial: || -->
			<div
				class="border border-white box-border"
				style="width: {cellSize}px; height: {cellSize}px;"
			>
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
				<div
					class="border border-white box-border"
					style="width: {cellSize}px; height: {cellSize}px;"
				></div>
				{#each row as cell, colIndex}
					<div
						class="border border-white box-border"
						style="width: {cellSize}px; height: {cellSize}px;"
					>
						<!-- Data cells - diagonal lines rendered in overlay -->
					</div>
				{/each}
				<div
					class="border border-white box-border"
					style="width: {cellSize}px; height: {cellSize}px;"
				></div>
			</div>
		{/each}

		<!-- Bottom row: BL fiducial, empty cells, BR fiducial -->
		<div class="flex">
			<!-- BL Fiducial: O -->
			<div
				class="border border-white box-border"
				style="width: {cellSize}px; height: {cellSize}px;"
			>
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
				<div
					class="border border-white box-border"
					style="width: {cellSize}px; height: {cellSize}px;"
				></div>
			{/each}
			<!-- BR Fiducial: ■ -->
			<div
				class="border border-white box-border"
				style="width: {cellSize}px; height: {cellSize}px;"
			>
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
		<svg
			class="absolute top-0 left-0 pointer-events-none"
			width={(gridSize + 2) * cellSize}
			height={(gridSize + 2) * cellSize}
			xmlns="http://www.w3.org/2000/svg"
		>
			<!-- Border lines connecting fiducials with gaps -->
			<!-- Top line: X to || -->
			<line
				x1={cellSize * 0.9 + gap}
				y1={cellSize * 0.5}
				x2={8 * cellSize + cellSize * 0.35 - gap}
				y2={cellSize * 0.5}
				stroke="#000"
				stroke-width={cellSize * 0.12}
				stroke-linecap="butt"
			/>
			<!-- Right line: || to ■ -->
			<line
				x1={8 * cellSize + cellSize * 0.5}
				y1={cellSize * 0.9 + gap}
				x2={8 * cellSize + cellSize * 0.5}
				y2={8 * cellSize + cellSize * 0.1 - gap}
				stroke="#000"
				stroke-width={cellSize * 0.12}
				stroke-linecap="butt"
			/>
			<!-- Bottom line: O to ■ -->
			<line
				x1={cellSize * 0.88 + gap}
				y1={8 * cellSize + cellSize * 0.5}
				x2={8 * cellSize + cellSize * 0.1 - gap}
				y2={8 * cellSize + cellSize * 0.5}
				stroke="#000"
				stroke-width={cellSize * 0.12}
				stroke-linecap="butt"
			/>
			<!-- Left line: X to O -->
			<line
				x1={cellSize * 0.5}
				y1={cellSize * 0.9 + gap}
				x2={cellSize * 0.5}
				y2={8 * cellSize + cellSize * 0.12 - gap}
				stroke="#000"
				stroke-width={cellSize * 0.12}
				stroke-linecap="butt"
			/>

			{#if diagonalLines.length > 0}
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
			{/if}
		</svg>
	</div>
</div>
