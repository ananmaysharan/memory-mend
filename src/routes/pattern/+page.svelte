<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import PatternEditor from '$lib/components/pattern/PatternEditor.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { mendStore } from '$lib/stores/mendStore.svelte';
	import { extractDiagonalLines } from '$lib/utils/diagonalOptimizer';
	import type { DiagonalLine } from '$lib/utils/diagonalOptimizer';

	// Animation state
	let isAnimating = $state(true);
	let animatedId = $state('000000');
	let animatedGrid = $state<boolean[][]>([]);

	const ANIMATION_DURATION = 2500; // 2.5 seconds
	const CHAR_CHANGE_INTERVAL = 80; // Change character every 80ms
	const GRID_UPDATE_INTERVAL = 60; // Update grid every 60ms

	// Pattern display settings (match PatternEditor)
	const cellSize = 28; // Large cell size
	const gridSize = 7;

	// Extract diagonal lines from animated grid
	const animatedDiagonalLines = $derived(
		isAnimating && animatedGrid.length > 0 ? extractDiagonalLines(animatedGrid) : []
	);

	const memoryDate = $derived(
		mendStore.memory?.timestamp
			? new Date(mendStore.memory.timestamp).toLocaleDateString('en-US', {
					year: 'numeric',
					month: 'long',
					day: 'numeric'
			  })
			: ''
	);

	// Create initial random grid (7x7 with corners as false)
	function createRandomGrid(): boolean[][] {
		const grid: boolean[][] = [];
		for (let r = 0; r < 7; r++) {
			const row: boolean[] = [];
			for (let c = 0; c < 7; c++) {
				const isCorner =
					(r === 0 && c === 0) ||
					(r === 0 && c === 6) ||
					(r === 6 && c === 0) ||
					(r === 6 && c === 6);
				row.push(isCorner ? false : Math.random() < 0.4);
			}
			grid.push(row);
		}
		return grid;
	}

	function randomBase36Char(): string {
		const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
		return chars[Math.floor(Math.random() * chars.length)];
	}

	async function playAnimation() {
		if (!mendStore.pattern) return;

		isAnimating = true;
		const startTime = Date.now();
		const finalId = mendStore.pattern.id;
		const finalGrid = mendStore.pattern.grid;

		// Initialize with random grid
		animatedGrid = createRandomGrid();

		// ID animation: Cycle random characters, progressively lock in final characters
		const idInterval = setInterval(() => {
			const progress = Math.min((Date.now() - startTime) / ANIMATION_DURATION, 1);
			const lockedChars = Math.floor(progress * 6); // 0 to 6

			animatedId = finalId
				.split('')
				.map((char, i) => {
					if (i < lockedChars) return char; // Locked
					return randomBase36Char(); // Still randomizing
				})
				.join('');

			if (progress >= 1) {
				clearInterval(idInterval);
				animatedId = finalId;
			}
		}, CHAR_CHANGE_INTERVAL);

		// Grid animation: Populate random X's, progressively match final pattern
		const gridInterval = setInterval(() => {
			const progress = Math.min((Date.now() - startTime) / ANIMATION_DURATION, 1);

			// Create grid that progressively matches final pattern
			animatedGrid = finalGrid.map((row, r) =>
				row.map((cell, c) => {
					const isCorner =
						(r === 0 && c === 0) ||
						(r === 0 && c === 6) ||
						(r === 6 && c === 0) ||
						(r === 6 && c === 6);
					if (isCorner) return false; // Corners always false

					// Use progress to blend random with final
					if (Math.random() < progress) {
						return cell; // Match final pattern
					} else {
						return Math.random() < 0.4; // Random X
					}
				})
			);

			if (progress >= 1) {
				clearInterval(gridInterval);
				animatedGrid = finalGrid;
				isAnimating = false;
			}
		}, GRID_UPDATE_INTERVAL);
	}

	onMount(async () => {
		if (!mendStore.pattern || !mendStore.memory) {
			goto('/capture');
			return;
		}

		// Only play animation on first visit (not when navigating back)
		if (!mendStore.patternAnimationShown) {
			await playAnimation();
			mendStore.patternAnimationShown = true;
		} else {
			// Show final pattern immediately
			isAnimating = false;
			animatedId = mendStore.pattern.id;
			animatedGrid = mendStore.pattern.grid;
		}
	});

	function handleContinue() {
		mendStore.goToPreview();
		goto('/preview');
	}
</script>

<div class="page">
	<TopBar title="Pattern" showBackButton={true} backDestination="/memory" />
	<div class="page-content">
		<!-- Header section with title and date -->
		<div class="flex gap-4 mb-6 items-start">
			<div class="flex-1">
				<h1 class="text-3xl font-cooper capitalize md:text-4xl mb-1">
					{mendStore.memory?.title || 'Your Memory'}
				</h1>
				<p class="text-xl text-gray-600 font-cooper">{memoryDate}</p>
			</div>
		</div>

		<!-- ID Display -->
		<div class="mb-6">
			<div class="bg-white border border-border rounded-lg py-4 flex flex-col items-center">
				<p class="text-s mb-2 font-mono text-gray-400 uppercase tracking-wide">Unique Pattern ID</p>
				<p class="text-3xl mb-0 font-fig text-black tracking-widest text-center">
					{isAnimating ? animatedId : mendStore.pattern?.id}
				</p>
			</div>
		</div>

		<!-- Pattern Display Section -->
		<div class="bg-white border border-border rounded-lg p-6 mb-6">
			{#if isAnimating && animatedGrid.length > 0}
				{@const gap = cellSize * 0.15}
				<!-- Animated pattern grid (matching PatternEditor structure exactly) -->
				<div class="flex flex-col items-center w-full">
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
						{#each animatedGrid as row, rowIndex}
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
							class="diagonal-overlay"
							width={(gridSize + 2) * cellSize}
							height={(gridSize + 2) * cellSize}
							style="position: absolute; top: 0; left: 0; pointer-events: none;"
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

							{#if animatedDiagonalLines.length > 0}
								{#each animatedDiagonalLines as line}
									{@const x1 =
										line.direction === 'nw-se'
											? (line.startCol + 1) * cellSize
											: (line.startCol + 2) * cellSize}
									{@const y1 = (line.startRow + 1) * cellSize}
									{@const x2 =
										line.direction === 'nw-se'
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
			{:else if mendStore.pattern}
				<!-- Final pattern with PatternEditor -->
				<PatternEditor pattern={mendStore.pattern} large={true} />
			{:else}
				<p>No pattern available</p>
			{/if}
		</div>

		<!-- Memory Details Section -->
		{#if mendStore.memory?.text || (mendStore.memory?.images && mendStore.memory.images.length > 0)}
			<div class="mb-6">
				<!-- Memory Text -->
				{#if mendStore.memory?.text}
					<div class="bg-white border border-border rounded-lg p-4 mb-6">
						<p class="font-cooper text-base m-0 italic">"{mendStore.memory.text}"</p>
					</div>
				{/if}

				<!-- Memory Images -->
				{#if mendStore.memory?.images && mendStore.memory.images.length > 0}
					<div class="grid grid-cols-3 md:grid-cols-5 gap-4">
						{#each mendStore.memory.images as image, index}
							<div class="relative bg-white p-2 md:p-3 shadow-sm aspect-square">
								<img
									src={image}
									alt="Memory {index + 1}"
									class="w-full h-full object-cover"
								/>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}

		<!-- Action Button -->
		<div class="flex flex-col gap-2.5">
			<Button onclick={handleContinue} disabled={isAnimating}>
				{isAnimating ? 'Generating...' : 'Proceed'}
			</Button>
		</div>
	</div>
</div>
