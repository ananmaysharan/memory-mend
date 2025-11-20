<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import PatternEditor from '$lib/components/pattern/PatternEditor.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { mendStore } from '$lib/stores/mendStore.svelte';

	onMount(() => {
		if (!mendStore.pattern || !mendStore.memory) {
			goto('/capture');
		}
	});

	function handleContinue() {
		mendStore.goToPreview();
		goto('/preview');
	}

	function goBack() {
		goto('/memory');
	}
</script>

<div class="page">
	<TopBar title="Review Pattern" showBackButton={true} backDestination="/memory" />
	<div class="page-content">

		<div class="flex flex-col gap-2.5">
			<div>
				<h2>Stitch Pattern</h2>
				{#if mendStore.pattern}
					<PatternEditor pattern={mendStore.pattern} />
				{:else}
					<p>No pattern available</p>
				{/if}
			</div>

			<div>
				{#if mendStore.memory?.text}
					<div>
						<h3>Memory</h3>
						<p>"{mendStore.memory.text}"</p>
					</div>
				{/if}

				<!-- {#if mendStore.image}
					<div>
						<h3>Repair</h3>
						<img src={mendStore.image} alt="Repair area" />
					</div>
				{/if} -->
			</div>
		</div>


		<div class="flex flex-col gap-2.5">
			<Button onclick={handleContinue}>Continue to Preview</Button>
			<Button onclick={goBack}>Back</Button>
		</div>
	</div>
</div>
