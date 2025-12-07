<script lang="ts">
	/**
	 * Manual Pattern Decode Page
	 */

	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import ManualPatternInput from '$lib/components/scan/ManualPatternInput.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';
	import { scanStore } from '$lib/stores/scanStore.svelte';
	import { gridToBinary } from '$lib/utils/hashUtils';
	import { findMendByPatternId as findInSupabase } from '$lib/services/supabase';

	// State
	let grid = $state<boolean[][]>([]);
	let error = $state<string | null>(null);
	let patternId = $state<string>('******');
	let scannedImage = $state<string | null>(null);
	let detectionError = $state<string | null>(null);

	onMount(() => {
		// Manual decode ONLY accessible via failed detection with image
		if (!scanStore.scannedImage) {
			goto('/scan'); // Redirect if no image (direct navigation blocked)
			return;
		}

		scannedImage = scanStore.scannedImage;
		detectionError = scanStore.detectionError;
		scanStore.clearScannedImage(); // Clear after reading
	});

	function handleGridComplete(completedGrid: boolean[][]) {
		grid = completedGrid;
		decodePattern();
	}

	function decodePattern() {
		error = null;

		// Check if grid has any data (at least one true value)
		const hasData = grid.some((row) => row.some((cell) => cell === true));

		if (!hasData) {
			// Grid is empty, show asterisks
			patternId = '******';
			return;
		}

		// Convert grid to binary
		const binary = gridToBinary(grid);

		// Progressively decode character by character
		const chars: string[] = [];
		const VALID_CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';

		for (let i = 0; i < 6; i++) {
			const start = i * 7;
			const chunk = binary.substring(start, start + 7);

			if (chunk.length < 7 || chunk === '0000000') {
				// Not enough bits or empty, show asterisk
				chars.push('*');
			} else {
				// Try to decode this chunk
				const paddedChunk = chunk.padEnd(7, '0');
				const asciiCode = parseInt('0' + paddedChunk, 2);
				const char = String.fromCharCode(asciiCode);

				// Only show if it's a valid base36 character
				if (VALID_CHARS.includes(char.toUpperCase())) {
					chars.push(char);
				} else {
					chars.push('*');
				}
			}
		}

		patternId = chars.join('');
	}

	async function unlockMend() {
		error = null;

		// 1. Try local lookup first
		let mend = historyStore.findMendByPatternId(patternId);

		// 2. If not found locally, try Supabase
		if (!mend) {
			try {
				const supabaseMend = await findInSupabase(patternId);

				// If found in Supabase, add to local history for offline access
				if (supabaseMend) {
					historyStore.addMend(supabaseMend);
					mend = supabaseMend;
				}
			} catch (err) {
				console.error('Supabase lookup error:', err);
				// Continue - will show "not found" below
			}
		}

		if (mend) {
			// Pattern found - navigate to mend detail page
			goto(`/history/${mend.id}`);
		} else {
			// Pattern not found in local or Supabase
			error = 'Pattern not found. Try again.';
		}
	}
</script>

<div class="page">
	<TopBar title="Decode" showBackButton={true} backDestination="/scan" />

	<div class="page-content">
		<!-- Detection Error Banner -->
		{#if detectionError}
			<div class="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
				<p class="text-yellow-800 font-medium mb-1">⚠️ Automatic Detection Failed</p>
				<p class="text-gray-600 text-sm">{detectionError}</p>
			</div>
		{/if}

		<!-- Instructions -->
		<p class="text-gray-600 mb-6">
			The pattern is shown behind the grid. Fill in the cells to match.
		</p>

		<!-- Manual Pattern Input with Background Image -->
		<div class="relative w-full max-w-md mx-auto flex justify-center mb-6">
			<img
				src={scannedImage}
				alt="Captured pattern"
				class="absolute inset-0 w-full h-full object-contain pointer-events-none"
				style="opacity: 0.3; z-index: 0;"
			/>

			<div class="relative" style="z-index: 1;">
				<ManualPatternInput onComplete={handleGridComplete} />
			</div>
		</div>

		<!-- Pattern ID Display -->
		<div class="mt-6 bg-white border border-border rounded-lg py-4 flex flex-col items-center">
			<p class="text-s mb-2 font-mono text-gray-400 uppercase tracking-wide">Decoded Pattern ID</p>
			<p class="text-3xl mb-0 font-fig text-black tracking-widest text-center">
				{patternId}
			</p>
		</div>

		<!-- Error Message -->
		{#if error}
			<p class="mt-4 text-red-800 text-sm text-center">{error}</p>
		{/if}

		<!-- Unlock Button (always visible) -->
		<div class="mt-6">
			<Button onclick={unlockMend}>Unlock Memory</Button>
		</div>
	</div>
</div>
