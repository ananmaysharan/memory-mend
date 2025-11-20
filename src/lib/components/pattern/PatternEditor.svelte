<script lang="ts">
	import type { PatternData } from '$lib/types/mend';
	import { getCornerMarker } from '$lib/utils/hashUtils';

	interface Props {
		pattern: PatternData;
	}

	let { pattern }: Props = $props();

	const cellSize = $derived(pattern.config.cellSize);
	const gridSize = $derived(pattern.config.gridSize);
</script>

<div>
	<!-- Pattern Info -->
	<div>
		<p><strong>Pattern ID:</strong> {pattern.id}</p>
	</div>

	<!-- Pattern Grid -->
	<div>
		{#each pattern.grid as row, rowIndex}
			<div style="display: flex;">
				{#each row as cell, colIndex}
					{@const cornerType = getCornerMarker(rowIndex, colIndex, gridSize)}
					<div class="cell" style="width: {cellSize}px; height: {cellSize}px; position: relative;">
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
									r={(cellSize - (cellSize * 0.1)) / 2}
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
	.cell {
		border: 1px solid #ddd;
		box-sizing: border-box;
	}
</style>
