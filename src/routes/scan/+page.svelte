<script lang="ts">
	/**
	 * Scan & Decode Page
	 * Allows users to manually input pattern and decode to find the associated memory
	 */

	import { goto } from '$app/navigation';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import ManualPatternInput from '$lib/components/scan/ManualPatternInput.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';
	import { gridToBinary, binaryToId } from '$lib/utils/hashUtils';

	// State
	let grid = $state<boolean[][]>([]);
	let error = $state<string | null>(null);
	let patternId = $state<string>('******');

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

		// Convert binary to ID
		const decodedId = binaryToId(binary);

		patternId = decodedId;
	}

	function unlockMend() {
		error = null;

		// Look up mend by pattern ID
		const mend = historyStore.findMendByPatternId(patternId);

		if (mend) {
			// Pattern found - navigate to mend detail page
			goto(`/history/${mend.id}`);
		} else {
			// Pattern not found
			error = 'Pattern not found. Try again.';
		}
	}
</script>

<div class="page">
	<TopBar title="Scan Mend" showBackButton={true} backDestination="/" />

	<div class="page-content">
		<h2 class="mb-4">Decode Pattern</h2>
		<p class="text-gray-600 mb-6">
			Fill out the memory mend pattern by tapping on the squares.
		</p>

		<!-- Manual Pattern Input -->
		<ManualPatternInput onComplete={handleGridComplete} />

		<!-- Pattern ID Display (always visible) -->
		<div class="mt-6">
			<div class="bg-white border-2 border-border rounded-lg py-4 flex flex-col items-center">
				<p class="text-s mb-2 font-mono text-gray-400 uppercase tracking-wide">Decoded Pattern ID</p>
				<p class="text-3xl mb-0 font-doto text-black font-bold tracking-widest text-center">
					{patternId}
				</p>
			</div>
		</div>

		<!-- Error Message -->
		{#if error}
			<p class="mt-4 text-red-800 text-sm text-center">{error}</p>
		{/if}

		<!-- Unlock Button (show when pattern is decoded, not asterisks) -->
		{#if patternId !== '******'}
			<div class="mt-6">
				<Button onclick={unlockMend}>Unlock Mend Memory</Button>
			</div>
		{/if}
	</div>
</div>
