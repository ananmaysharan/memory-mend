<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/ui/Button.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import ImageStack from '$lib/components/memory/ImageStack.svelte';
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
			<div class="grid grid-cols-2 md:grid-cols-3 gap-5 mt-5">
				{#each mends as mend (mend.id)}
					<div
						class="flex flex-col gap-2 cursor-pointer"
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
							<ImageStack
								images={mend.memory.images && mend.memory.images.length > 0 ? [mend.image, ...mend.memory.images] : [mend.image]}
								maxVisible={3}
							/>
						{/if}

						<h3 class="font-cooper text-lg font-semibold mb-0 mt-2 capitalize">
							{mend.memory.title || 'Untitled Memory'}
						</h3>

						<p class='text-xs text-gray-500 mb-0'>{formatDate(mend.createdAt)}</p>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
