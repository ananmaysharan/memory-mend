<script lang="ts">
	/**
	 * Hidden Testing Route for Custom Pattern Generation
	 * Accessible only via direct URL: /testing
	 */

	import { downloadPatternSVG } from '$lib/services/svgGenerator';
	import type { PatternData } from '$lib/types/mend';

	const GRID_SIZE = 7;
	const CELL_SIZE = 28;

	// Initialize 7x7 grid with all false
	let grid = $state<boolean[][]>(
		Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(false))
	);

	// Custom pattern ID input
	let customId = $state('TEST01');

	// Toggle cell
	function toggleCell(row: number, col: number) {
		grid[row][col] = !grid[row][col];
	}

	// Clear all cells
	function clearGrid() {
		grid = Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(false));
	}

	// Fill random pattern
	function randomPattern() {
		grid = Array(GRID_SIZE).fill(null).map(() =>
			Array(GRID_SIZE).fill(null).map(() => Math.random() < 0.4)
		);
	}

	// Download pattern as SVG
	function handleDownload() {
		const pattern: PatternData = {
			grid: grid,
			id: customId,
			config: {
				gridSize: GRID_SIZE,
				cellSize: CELL_SIZE
			}
		};
		downloadPatternSVG(pattern, CELL_SIZE);
	}

	// Calculate gap for fiducial borders
	const gap = $derived(CELL_SIZE * 0.15);
	const strokeColor = '#000';
</script>

<div class="min-h-screen bg-gray-100 p-8">
	<div class="max-w-lg mx-auto">
		<h1 class="text-2xl font-bold mb-2">Pattern Generator (Testing)</h1>
		<p class="text-gray-600 mb-6 text-sm">Hidden route for generating custom patterns</p>

		<!-- Pattern ID Input -->
		<div class="mb-6">
			<label class="block text-sm font-medium mb-2" for="pattern-id">Pattern ID</label>
			<input
				id="pattern-id"
				type="text"
				bind:value={customId}
				maxlength="6"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
				placeholder="Enter pattern ID"
			/>
		</div>

		<!-- Grid Editor -->
		<div class="bg-white border border-gray-300 rounded-lg p-6 mb-6">
			<div class="flex flex-col items-center w-full">
				<div class="inline-flex flex-col relative">
					<!-- Top row: TL fiducial, empty cells, TR fiducial -->
					<div class="flex">
						<!-- TL Fiducial: X -->
						<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;">
							<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
								<line
									x1={CELL_SIZE * 0.1}
									y1={CELL_SIZE * 0.1}
									x2={CELL_SIZE * 0.9}
									y2={CELL_SIZE * 0.9}
									stroke={strokeColor}
									stroke-width={CELL_SIZE * 0.12}
									stroke-linecap="butt"
								/>
								<line
									x1={CELL_SIZE * 0.9}
									y1={CELL_SIZE * 0.1}
									x2={CELL_SIZE * 0.1}
									y2={CELL_SIZE * 0.9}
									stroke={strokeColor}
									stroke-width={CELL_SIZE * 0.12}
									stroke-linecap="butt"
								/>
							</svg>
						</div>
						{#each Array(GRID_SIZE) as _, i (i)}
							<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"></div>
						{/each}
						<!-- TR Fiducial: || -->
						<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;">
							<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
								<line
									x1={CELL_SIZE * 0.35}
									y1={CELL_SIZE * 0.1}
									x2={CELL_SIZE * 0.35}
									y2={CELL_SIZE * 0.9}
									stroke={strokeColor}
									stroke-width={CELL_SIZE * 0.12}
									stroke-linecap="butt"
								/>
								<line
									x1={CELL_SIZE * 0.65}
									y1={CELL_SIZE * 0.1}
									x2={CELL_SIZE * 0.65}
									y2={CELL_SIZE * 0.9}
									stroke={strokeColor}
									stroke-width={CELL_SIZE * 0.12}
									stroke-linecap="butt"
								/>
							</svg>
						</div>
					</div>

					<!-- Middle rows: empty cell, 7x7 data grid, empty cell -->
					{#each grid as row, rowIndex (rowIndex)}
						<div class="flex">
							<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"></div>
							{#each row as cell, colIndex (colIndex)}
								<div
									class="border box-border cursor-pointer hover:bg-gray-50 transition-colors"
									style="border-color: {strokeColor}; width: {CELL_SIZE}px; height: {CELL_SIZE}px;"
									onclick={() => toggleCell(rowIndex, colIndex)}
									role="button"
									tabindex="0"
									onkeydown={(e) => {
										if (e.key === 'Enter' || e.key === ' ') {
											toggleCell(rowIndex, colIndex);
										}
									}}
								>
									{#if cell}
										<!-- Show diagonal X when cell is active -->
										<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
											<line
												x1={0}
												y1={0}
												x2={CELL_SIZE}
												y2={CELL_SIZE}
												stroke={strokeColor}
												stroke-width={CELL_SIZE * 0.12}
												stroke-linecap="butt"
											/>
											<line
												x1={CELL_SIZE}
												y1={0}
												x2={0}
												y2={CELL_SIZE}
												stroke={strokeColor}
												stroke-width={CELL_SIZE * 0.12}
												stroke-linecap="butt"
											/>
										</svg>
									{/if}
								</div>
							{/each}
							<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"></div>
						</div>
					{/each}

					<!-- Bottom row: BL fiducial, empty cells, BR fiducial -->
					<div class="flex">
						<!-- BL Fiducial: O -->
						<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;">
						<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
							<circle
								cx={CELL_SIZE / 2}
								cy={CELL_SIZE / 2}
								r={(CELL_SIZE - CELL_SIZE * 0.24) / 2}
								fill="none"
								stroke={strokeColor}
									stroke-width={CELL_SIZE * 0.12}
								/>
							</svg>
						</div>
						{#each Array(GRID_SIZE) as _, i (i)}
							<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"></div>
						{/each}
						<!-- BR Fiducial: square -->
						<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;">
						<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
							<rect
								x={CELL_SIZE * 0.1}
								y={CELL_SIZE * 0.1}
								width={CELL_SIZE * 0.8}
								height={CELL_SIZE * 0.8}
								fill="none"
								stroke={strokeColor}
									stroke-width={CELL_SIZE * 0.12}
								/>
							</svg>
						</div>
					</div>

					<!-- Border lines connecting fiducials (matching PatternEditor) -->
					<svg
						class="absolute top-0 left-0 pointer-events-none"
						width={(GRID_SIZE + 2) * CELL_SIZE}
						height={(GRID_SIZE + 2) * CELL_SIZE}
						xmlns="http://www.w3.org/2000/svg"
					>
						<!-- Top line: X to || -->
						<line
							x1={CELL_SIZE * 0.9 + gap}
							y1={CELL_SIZE * 0.5}
							x2={8 * CELL_SIZE + CELL_SIZE * 0.35 - gap}
							y2={CELL_SIZE * 0.5}
							stroke={strokeColor}
							stroke-width={CELL_SIZE * 0.12}
							stroke-linecap="butt"
						/>
						<!-- Right line: || to square -->
						<line
							x1={8 * CELL_SIZE + CELL_SIZE * 0.5}
							y1={CELL_SIZE * 0.9 + gap}
							x2={8 * CELL_SIZE + CELL_SIZE * 0.5}
							y2={8 * CELL_SIZE + CELL_SIZE * 0.1 - gap}
							stroke={strokeColor}
							stroke-width={CELL_SIZE * 0.12}
							stroke-linecap="butt"
						/>
						<!-- Bottom line: O to square -->
						<line
							x1={CELL_SIZE * 0.88 + gap}
							y1={8 * CELL_SIZE + CELL_SIZE * 0.5}
							x2={8 * CELL_SIZE + CELL_SIZE * 0.1 - gap}
							y2={8 * CELL_SIZE + CELL_SIZE * 0.5}
							stroke={strokeColor}
							stroke-width={CELL_SIZE * 0.12}
							stroke-linecap="butt"
						/>
						<!-- Left line: X to O -->
						<line
							x1={CELL_SIZE * 0.5}
							y1={CELL_SIZE * 0.9 + gap}
							x2={CELL_SIZE * 0.5}
							y2={8 * CELL_SIZE + CELL_SIZE * 0.12 - gap}
							stroke={strokeColor}
							stroke-width={CELL_SIZE * 0.12}
							stroke-linecap="butt"
						/>
					</svg>
				</div>
			</div>
		</div>

		<!-- Action Buttons -->
		<div class="flex flex-col gap-3">
			<button
				onclick={handleDownload}
				class="w-full bg-black text-white py-3 px-4 rounded-lg font-medium hover:bg-gray-800 transition-colors"
			>
				Download SVG
			</button>
			<div class="flex gap-3">
				<button
					onclick={clearGrid}
					class="flex-1 bg-gray-200 text-gray-800 py-2 px-4 rounded-lg font-medium hover:bg-gray-300 transition-colors"
				>
					Clear
				</button>
				<button
					onclick={randomPattern}
					class="flex-1 bg-gray-200 text-gray-800 py-2 px-4 rounded-lg font-medium hover:bg-gray-300 transition-colors"
				>
					Random
				</button>
			</div>
		</div>
	</div>
</div>
