<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';

	const mend = $derived(historyStore.mends.find((m) => m.id === $page.params.id));

	function formatDate(timestamp: number): string {
		return new Date(timestamp).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric'
		});
	}

	// Redirect if mend not found
	$effect(() => {
		if (!mend && historyStore.mends.length > 0) {
			goto('/profile');
		}
	});
</script>

<div class="page">
	<TopBar title="Mend" showBackButton backDestination="/profile" />

	{#if mend}
		<div class="page-content">
			<div class="max-w-md mx-auto">
				<!-- Post header -->
				<div class="flex items-center justify-between mb-3">
					<div class="flex items-center gap-2">
						<div class="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center">
							<span class="font-mono text-xs text-orange-600">Y</span>
						</div>
						<span class="font-mono text-sm text-gray-700">Your Memory Mend</span>
					</div>
					<span class="text-sm text-gray-400 font-mono">{formatDate(mend.createdAt)}</span>
				</div>

				<!-- Memory title -->
				<h3 class="font-cooper text-lg font-semibold mb-3 capitalize">
					{mend.memory.title || 'Untitled Memory'}
				</h3>

				<!-- Polaroid image -->
				{#if mend.image}
					<div class="bg-white p-3 shadow-md w-full mb-4">
						<img
							src={mend.image}
							alt={mend.memory.title || 'Mend'}
							class="w-full aspect-square object-cover"
						/>
					</div>
				{/if}

				<!-- Memory text if exists -->
				{#if mend.memory.text}
					<div class="bg-white border border-border rounded-lg p-4">
						<p class="text-sm text-gray-600 mb-0 italic">{mend.memory.text}</p>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>
