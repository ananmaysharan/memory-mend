<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/ui/Button.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { mendStore } from '$lib/stores/mendStore.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';

	const mends = $derived(historyStore.getSortedMends());

	function startNewMend() {
		mendStore.reset();
		goto('/capture');
	}

	function formatDate(timestamp: number): string {
		return new Date(timestamp).toLocaleDateString();
	}
</script>

<div class="page">
	<TopBar title="Memory Mend" />
	<div class="page-content">
		<div class="mt-5 flex gap-3 md:flex-row flex-col">
			<Button onclick={startNewMend}>Start New Mend</Button>
			<Button>Scan Mend</Button>
		</div>

		<h2 class='my-5'> Your Memory Mends </h2>

		{#if mends.length <= 0}
			<p>Start or scan a mend to add to your library.</p>
		{/if}

		{#if mends.length > 0}

			<div class="grid grid-cols-3 gap-5">
				{#each mends.slice(0, 6) as mend (mend.id)}
					<div
						class="flex flex-col gap-2 p-3 cursor-pointer"
						onclick={() => goto(`/history/${mend.id}?from=home`)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								goto(`/history/${mend.id}?from=home`);
							}
						}}
					>
						{#if mend.image}
							<img src={mend.image} alt="Mend" />
						{/if}

						{#if mend.memory.text}
							<p class="italic mb-0">"{mend.memory.text}"</p>
						{:else}
							<p>Image memory</p>
						{/if}

						<p class='text-xs mb-0'>{formatDate(mend.createdAt)}</p>
					</div>
				{/each}
			</div>

			{#if mends.length > 9}
				<div class="mt-5">
					<Button onclick={() => goto('/history')}>View Full Mend Library</Button>
				</div>
			{/if}
		{/if}
	</div>
</div>
