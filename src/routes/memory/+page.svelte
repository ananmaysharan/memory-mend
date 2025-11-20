<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import type { Memory } from '$lib/types/mend';
	import MemoryInput from '$lib/components/memory/MemoryInput.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { mendStore } from '$lib/stores/mendStore.svelte';

	onMount(() => {
		if (!mendStore.image) {
			goto('/capture');
		}
	});

	async function handleMemorySubmit(memory: Memory) {
		await mendStore.setMemory(memory);
		goto('/pattern');
	}
</script>

<div class="page">
	<TopBar title="Add Your Memory" showBackButton={true} backDestination="/detection" />
	<div class="page-content">

		{#if mendStore.image}
			<div class="mb-5">
				<img src={mendStore.image} alt="Captured repair area"/>
			</div>
		{/if}

		<MemoryInput onSubmit={handleMemorySubmit} />

		</div>
</div>
