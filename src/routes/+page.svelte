<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/ui/Button.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import ImageStack from '$lib/components/memory/ImageStack.svelte';
	import { mendStore } from '$lib/stores/mendStore.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';
	import Scan from "phosphor-svelte/lib/Scan";
	import PlusCircle from "phosphor-svelte/lib/PlusCircle";
	import BookOpen from "phosphor-svelte/lib/BookOpen";

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
			<Button onclick={startNewMend}><PlusCircle size={18} weight="bold" />Start New Mend</Button>
			<Button><Scan size={18} weight="bold" />Scan Mend</Button>
		</div>

		<h2 class='my-5'> Your Memory Mends </h2>

		{#if mends.length <= 0}
			<p>Start or scan a mend to add to your library.</p>
		{/if}

		{#if mends.length > 0}
			<div class="grid grid-cols-2 md:grid-cols-3 gap-5">
				{#each mends.slice(0, 6) as mend (mend.id)}
					<div
						class="flex flex-col gap-2 cursor-pointer"
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

			{#if mends.length > 6}
				<div class="mt-5">
					<Button onclick={() => goto('/history')}><BookOpen size={18} weight="bold" />View Full Mend Library</Button>
				</div>
			{/if}
		{/if}
	</div>
</div>

<style>
	.single-image {
		aspect-ratio: 1;
		overflow: hidden;
	}

	.single-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
</style>
