<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import PatternEditor from '$lib/components/pattern/PatternEditor.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { mendStore } from '$lib/stores/mendStore.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';
	import { downloadPatternSVG } from '$lib/services/svgGenerator';

	const memoryDate = $derived(
		mendStore.memory?.timestamp
			? new Date(mendStore.memory.timestamp).toLocaleDateString('en-US', {
					year: 'numeric',
					month: 'long',
					day: 'numeric'
			  })
			: ''
	);

	onMount(() => {
		if (!mendStore.pattern) {
			goto('/capture');
		}
	});

	async function handleSendToPi() {
		alert('Raspberry Pi integration coming soon!');
	}

	function handleDownloadSVG() {
		if (mendStore.pattern) {
			downloadPatternSVG(mendStore.pattern, 28);
		}
	}

	function handleSaveAndFinish() {
		try {
			const mend = mendStore.getMend();
			historyStore.addMend({
				...mend,
				status: 'ready'
			});
			mendStore.reset();
			goto('/');
		} catch (error) {
			console.error('Failed to save mend:', error);

			// Show user-friendly error message
			const errorMessage = error instanceof Error ? error.message : 'Unknown error';

			if (errorMessage.includes('quota') || errorMessage.includes('storage')) {
				alert(
					'Failed to save: Storage is full.\n\n' +
					'Your memory has too many or too large images. Try:\n' +
					'• Going back and removing some images\n' +
					'• Using fewer images\n\n' +
					'Note: Your progress has not been lost - you can go back and modify your memory.'
				);
			} else {
				alert(`Failed to save mend: ${errorMessage}`);
			}
		}
	}
</script>

<div class="page">
	<TopBar title="Preview & Send" showBackButton={true} backDestination="/pattern" />
	<div class="page-content">
		<!-- Header section with title, date, and garment info -->
		<div class="mb-6">
			<h1 class="text-3xl md:text-4xl mb-1 font-cooper capitalize">
				{mendStore.memory?.title || 'Your Memory'}
			</h1>
			<p class="text-xl text-gray-600 font-cooper">{memoryDate}</p>
			{#if mendStore.garmentType || mendStore.material}
				<p class="text-lg text-gray-500 capitalize mt-2 font-mono uppercase">
					{#if mendStore.material && mendStore.garmentType}
						{mendStore.material} {mendStore.garmentType}
					{:else if mendStore.garmentType}
						{mendStore.garmentType}
					{:else if mendStore.material}
						{mendStore.material}
					{/if}
				</p>
			{/if}
		</div>

		<!-- Pattern Display Section -->
		<div class="bg-white border border-border rounded-lg p-6 mb-6">
			{#if mendStore.pattern}
				<PatternEditor pattern={mendStore.pattern} large={true} />
			{/if}
		</div>

		<!-- Action Buttons -->
		<div class="flex gap-2.5 flex-col">
			<Button onclick={handleDownloadSVG}>Download SVG</Button>
			<Button onclick={handleSendToPi}>Send to Pi</Button>
			<Button onclick={handleSaveAndFinish}>Save & Finish</Button>
		</div>
	</div>
</div>
