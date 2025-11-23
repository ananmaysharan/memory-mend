<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/ui/Button.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';

	const mends = $derived(historyStore.getSortedMends());

	function formatDate(timestamp: number): string {
		return new Date(timestamp).toLocaleDateString();
	}
</script>

<div class="page">
	<TopBar title="Mend Library" showBackButton={true} backDestination="/" />
	<div class="page-content">
		<p>All your memory mends in one place.</p>

		{#if mends.length === 0}
			<div class="mt-5">
				<Button onclick={() => goto('/capture')}>Create Memory Mend</Button>
			</div>
		{:else}
			<div class="grid grid-cols-3 gap-5 mt-5">
				{#each mends as mend (mend.id)}
					<div
						style="border: 1px solid #ddd; padding: 15px; cursor: pointer;"
						onclick={() => goto(`/history/${mend.id}?from=library`)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								goto(`/history/${mend.id}?from=library`);
							}
						}}
					>
						{#if mend.image}
							<img src={mend.image} alt="Mend" class="mb-2.5" />
						{/if}

						{#if mend.memory.text}
							<p class="mb-2.5" style="font-style: italic;">"{mend.memory.text}"</p>
						{:else}
							<p class="mb-2.5">Image memory</p>
						{/if}

						<p style="font-size: 12px; color: #999;">{formatDate(mend.createdAt)}</p>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
