<script lang="ts">
	import type { PatternData } from '$lib/types/mend';
	import { getCornerMarker } from '$lib/utils/hashUtils';

	interface Props {
		pattern: PatternData;
		large?: boolean;
	}

	let { pattern, large = false }: Props = $props();

	// Calculate cell size based on display mode
	const baseCellSize = $derived(large ? 28 : pattern.config.cellSize);
	const cellSize = $derived(baseCellSize);
	const gridSize = $derived(pattern.config.gridSize);
</script>

<div class="pattern-container">
	<!-- Pattern Info -->
	<div class="mb-4 text-center">
		<p class="font-mono text-sm text-gray-600 m-0">
			<strong>Pattern ID:</strong>
			{pattern.id}
		</p>
	</div>

	<!-- Pattern Grid -->
	<div class="pattern-grid">
		{#each pattern.grid as row, rowIndex}
			<div class="flex">
				{#each row as cell, colIndex}
					{@const cornerType = getCornerMarker(rowIndex, colIndex, gridSize)}
					<div
						class="cell"
						style="width: {cellSize}px; height: {cellSize}px; position: relative;"
					>
						{#if cornerType === 'TL'}
							<!-- Top-left: X pattern -->
							<svg width={cellSize} height={cellSize} xmlns="http://www.w3.org/2000/svg">
								<line
									x1={cellSize * 0.1}
									y1={cellSize * 0.1}
									x2={cellSize * 0.9}
									y2={cellSize * 0.9}
									stroke="#000"
									stroke-width={cellSize * 0.1}
								/>
								<line
									x1={cellSize * 0.9}
									y1={cellSize * 0.1}
									x2={cellSize * 0.1}
									y2={cellSize * 0.9}
									stroke="#000"
									stroke-width={cellSize * 0.1}
								/>
							</svg>
						{:else if cornerType === 'TR'}
							<!-- Top-right: || pattern -->
							<svg width={cellSize} height={cellSize} xmlns="http://www.w3.org/2000/svg">
								<line
									x1={cellSize * 0.35}
									y1={cellSize * 0.1}
									x2={cellSize * 0.35}
									y2={cellSize * 0.9}
									stroke="#000"
									stroke-width={cellSize * 0.1}
								/>
								<line
									x1={cellSize * 0.65}
									y1={cellSize * 0.1}
									x2={cellSize * 0.65}
									y2={cellSize * 0.9}
									stroke="#000"
									stroke-width={cellSize * 0.1}
								/>
							</svg>
						{:else if cornerType === 'BL'}
							<!-- Bottom-left: O pattern (circle) -->
							<svg width={cellSize} height={cellSize} xmlns="http://www.w3.org/2000/svg">
								<circle
									cx={cellSize / 2}
									cy={cellSize / 2}
									r={(cellSize - cellSize * 0.1) / 2}
									fill="none"
									stroke="#000"
									stroke-width={cellSize * 0.1}
								/>
							</svg>
						{:else if cornerType === 'BR'}
							<!-- Bottom-right: solid square -->
							<div style="width: 100%; height: 100%; background-color: #000;"></div>
						{:else if cell}
							<!-- Data cell with stitch (X mark) -->
							<svg width={cellSize} height={cellSize} xmlns="http://www.w3.org/2000/svg">
								<line
									x1="0"
									y1="0"
									x2={cellSize}
									y2={cellSize}
									stroke="#000"
									stroke-width={cellSize * 0.12}
									stroke-linecap="butt"
								/>
								<line
									x1={cellSize}
									y1="0"
									x2="0"
									y2={cellSize}
									stroke="#000"
									stroke-width={cellSize * 0.12}
									stroke-linecap="butt"
								/>
							</svg>
						{/if}
					</div>
				{/each}
			</div>
		{/each}
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
		border: 2px solid #333;
		background: white;
	}

	.cell {
		border: 1px solid #ddd;
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
