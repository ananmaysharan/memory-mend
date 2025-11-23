<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import PatternEditor from '$lib/components/pattern/PatternEditor.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { mendStore } from '$lib/stores/mendStore.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';

	onMount(() => {
		if (!mendStore.pattern) {
			goto('/capture');
		}
	});

	async function handleSendToPi() {
		alert('Raspberry Pi integration coming soon!');
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

	function goBack() {
		goto('/pattern');
	}
</script>

<div class="page">
	<TopBar title="Preview & Send" showBackButton={true} backDestination="/pattern" />
	<div class="page-content">
		<p>Review your pattern before sending to the embroidery machine</p>

		{#if mendStore.garmentType || mendStore.material}
			<p class="text-sm text-gray-600 capitalize">
				{#if mendStore.material && mendStore.garmentType}
					{mendStore.material} {mendStore.garmentType}
				{:else if mendStore.garmentType}
					{mendStore.garmentType}
				{:else if mendStore.material}
					{mendStore.material}
				{/if}
			</p>
		{/if}

		<hr />

		<div>
			<h2>Final Pattern</h2>
			{#if mendStore.pattern}
				<PatternEditor pattern={mendStore.pattern} />
			{/if}
		</div>

		<hr />

		<div class="flex gap-2.5 flex-col">
			<Button onclick={handleSendToPi}>Send to Pi</Button>
			<Button onclick={handleSaveAndFinish}>Save & Finish</Button>
			<Button onclick={goBack}>Back</Button>
		</div>
	</div>
</div>
