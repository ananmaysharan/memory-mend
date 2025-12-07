<script lang="ts">
	/**
	 * Pattern Analysis Page - Detects and decodes pattern from captured image
	 */

	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';
	import { scanStore } from '$lib/stores/scanStore.svelte';
	import { gridToBinary } from '$lib/utils/hashUtils';
	import { findMendByPatternId as findInSupabase } from '$lib/services/supabase';

	// Get image from scan store
	let capturedImage = $state<string | null>(null);
	let isScanning = $state(true);
	let error = $state<string | null>(null);
	let grid = $state<boolean[][]>([]);
	let patternId = $state<string>('******');
	let foundMend = $state<any>(null);

	onMount(async () => {
		// Get image from scan store
		if (!scanStore.scannedImage) {
			goto('/scan');
			return;
		}

		capturedImage = scanStore.scannedImage;
		// Don't clear scanStore yet - keep image for potential manual decode fallback

		// Start pattern detection
		try {
			const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001';

			const response = await fetch(`${apiUrl}/detect-pattern`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ image: capturedImage })
			});

			if (!response.ok) {
				throw new Error('Pattern detection failed');
			}

			const result = await response.json();
			console.log('Detection result:', result);
			console.log('Grid row 0:', result.grid[0]);
			console.log('Grid row 0 cell types:', result.grid[0].map((c: any) => typeof c));

			grid = result.grid;
			isScanning = false;

			// Always decode the pattern (even if confidence is low)
			decodePattern();

			// Check if pattern was fully decoded (no asterisks)
			if (patternId.includes('*')) {
				// Incomplete decoding - navigate to manual decode
				scanStore.setDetectionError(
					'Could not decode complete pattern. Please manually fill the grid.'
				);
				goto('/scan/manual');
				return;
			}

			// Check confidence AFTER decoding
			if (result.confidence < 0.6) {
				// Low confidence - navigate to manual decode
				scanStore.setDetectionError(
					`Low confidence (${(result.confidence * 100).toFixed(0)}%). Please verify the pattern.`
				);
				goto('/scan/manual');
				return;
			}

			// Look up the mend
			await lookupMend();
		} catch (err) {
			console.error('Pattern detection error:', err);

			// Set error message and navigate to manual decode
			scanStore.setDetectionError(
				err instanceof TypeError
					? 'Cannot reach detection service. Please check your connection.'
					: 'Pattern detection failed. Please manually fill the grid.'
			);
			goto('/scan/manual');
		}
	});

	function decodePattern() {
		console.log('Decoding pattern from grid');

		// Snapshot the grid to get actual values (not proxy)
		const gridData = $state.snapshot(grid);

		// Debug: Print grid as ASCII
		console.log('Grid visualization:');
		for (let i = 0; i < gridData.length; i++) {
			const row = gridData[i];
			const visual = row.map((cell, j) => {
				const isCorner = (i === 0 && j === 0) || (i === 0 && j === 6) || (i === 6 && j === 0) || (i === 6 && j === 6);
				if (isCorner) return '·';
				return cell ? '█' : '·';
			}).join(' ');
			console.log(`  Row ${i}: ${visual} [${row.map(c => c ? '1' : '0').join('')}]`);
		}

		// Check if grid has any data
		const hasData = gridData.some((row) => row.some((cell) => cell));

		if (!hasData) {
			console.log('Grid has no data (all false)');
			patternId = '******';
			return;
		}

		// Convert grid to binary
		const binary = gridToBinary(gridData);
		console.log('Binary string:', binary);

		// Decode character by character
		const chars: string[] = [];
		const VALID_CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';

		for (let i = 0; i < 6; i++) {
			const start = i * 7;
			const chunk = binary.substring(start, start + 7);

			if (chunk.length < 7 || chunk === '0000000') {
				chars.push('*');
			} else {
				const paddedChunk = chunk.padEnd(7, '0');
				// Match testing script: no leading 0
				const asciiCode = parseInt(paddedChunk, 2);
				const char = String.fromCharCode(asciiCode);

				if (VALID_CHARS.includes(char.toUpperCase())) {
					chars.push(char);
				} else {
					chars.push('*');
				}
			}
		}

		patternId = chars.join('');
		console.log('Decoded pattern ID:', patternId);
	}

	async function lookupMend() {
		// Try local lookup first
		let mend = historyStore.findMendByPatternId(patternId);

		// If not found locally, try Supabase
		if (!mend) {
			try {
				const supabaseMend = await findInSupabase(patternId);
				if (supabaseMend) {
					historyStore.addMend(supabaseMend);
					mend = supabaseMend;
				}
			} catch (err) {
				console.error('Supabase lookup error:', err);
			}
		}

		foundMend = mend;
		console.log('Pattern lookup:', patternId, foundMend ? 'found' : 'not found');
	}

	function handleTryAgain() {
		goto('/scan');
	}

	function handleViewMend() {
		if (foundMend) {
			// Clear scanStore on successful detection
			scanStore.clearScannedImage();
			goto(`/history/${foundMend.id}`);
		}
	}
</script>

<div class="page">
	<TopBar title="Scanning" showBackButton={true} backDestination="/scan" />

	<div class="page-content">
		<!-- Captured Image with Scanning Animation -->
		{#if capturedImage}
			<div class="relative w-full max-w-md mx-auto overflow-hidden rounded bg-surface mb-6" style="aspect-ratio: 3/4;">
				<img
					src={capturedImage}
					alt="Captured pattern"
					class="w-full h-full object-contain"
				/>
				{#if isScanning}
					<div class="scanning-bar"></div>
				{/if}
			</div>
		{/if}

		<!-- Status Text -->
		{#if isScanning}
			<p class="text-center text-gray-600 mb-6">Detecting pattern...</p>
		{:else}
			<!-- Pattern ID Display - Show whenever pattern has been decoded -->
			{#if patternId && patternId !== '******'}
				<div class="mb-6">
					<div class="bg-white border border-border rounded-lg py-4 flex flex-col items-center">
						<p class="text-s mb-2 font-mono text-gray-400 uppercase tracking-wide">Decoded Pattern ID</p>
						<p class="text-3xl mb-0 font-fig text-black tracking-widest text-center">
							{patternId}
						</p>
					</div>
				</div>
			{/if}

			<!-- Error/Warning Message -->
			{#if error}
				<div class="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
					<p class="text-yellow-800 font-medium mb-1">⚠️ Detection Warning</p>
					<p class="text-gray-600 text-sm">{error}</p>
				</div>
			{/if}

			<!-- Result - Show if pattern was decoded -->
			{#if patternId && patternId !== '******'}
				{#if foundMend}
					<div class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
						<p class="text-green-800 font-medium mb-2">✅ Memory Found!</p>
						<p class="text-gray-700 mb-1"><strong>{foundMend.title || 'Untitled'}</strong></p>
						{#if foundMend.text}
							<p class="text-gray-600 text-sm line-clamp-2">{foundMend.text}</p>
						{/if}
					</div>
					<Button onclick={handleViewMend}>View Full Memory</Button>
				{:else}
					<div class="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
						<p class="text-gray-800 font-medium mb-2">Pattern not found</p>
						<p class="text-gray-600 text-sm">This pattern is not in your library or the global database.</p>
					</div>
					<Button onclick={handleTryAgain}>Scan Another Pattern</Button>
				{/if}
			{:else}
				<!-- Complete failure - couldn't decode pattern at all -->
				<div class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
					<p class="text-red-800 font-medium mb-2">❌ Detection Failed</p>
					<p class="text-gray-600 text-sm">Could not decode pattern from image. Please try again with better lighting or a clearer view.</p>
				</div>
				<Button onclick={handleTryAgain}>Try Again</Button>
			{/if}
		{/if}
	</div>
</div>

<style>
	.scanning-bar {
		position: absolute;
		left: 0;
		right: 0;
		height: 4px;
		background: var(--color-blue);
		box-shadow: 0 0 8px rgba(173, 215, 247, 0.6);
		animation: scan 2s ease-in-out infinite;
	}

	@keyframes scan {
		0%,
		100% {
			top: 0;
		}
		50% {
			top: calc(100% - 4px);
		}
	}

	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
