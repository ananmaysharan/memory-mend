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
		const mend = mendStore.getMend();
		historyStore.addMend({
			...mend,
			status: 'ready'
		});
		mendStore.reset();
		goto('/');
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
