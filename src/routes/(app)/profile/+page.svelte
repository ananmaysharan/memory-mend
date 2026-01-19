<script lang="ts">
	import { goto } from '$app/navigation';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import ImageStack from '$lib/components/memory/ImageStack.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';
	import User from 'phosphor-svelte/lib/User';

	const mends = $derived(historyStore.getSortedMends());
	const publicMends = $derived(mends.filter((m) => m.isPublic));
	const mendCount = $derived(mends.length);

	function formatDate(timestamp: number): string {
		return new Date(timestamp).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric'
		});
	}
</script>

<div class="page">
	<TopBar title="Profile" />
	<div class="page-content">
		<!-- Profile Header -->
		<div class="flex flex-col items-center gap-3 py-6">
			<div class="w-24 h-24 rounded-full bg-orange-100 flex items-center justify-center">
				<User size={40} weight="light" class="text-orange-600" />
			</div>
			<div class="text-center">
				<h1 class="font-fig text-2xl uppercase mb-0">@MDE-USER</h1>
			</div>
		</div>

		<!-- Stats Row -->
		<div class="flex justify-around py-4 bg-white border border-border rounded-lg mb-6">
			<div class="flex flex-col items-center gap-1">
				<span class="font-cooper text-xl font-semibold">{mendCount}</span>
				<span class="text-xs text-gray-500 font-mono uppercase">Mends</span>
			</div>
			<!-- <div class="w-px bg-border"></div> -->
			<div class="flex flex-col items-center gap-1">
				<span class="font-cooper text-xl font-semibold">5</span>
				<span class="text-xs text-gray-500 font-mono uppercase">Friends</span>
			</div>
		</div>

		<!-- Your Mends Section -->
		<div class="mb-6">
			<h2 class="text-lg font-cooper font-semibold mb-4">Your Memory Mends</h2>

			{#if mends.length === 0}
				<div class="bg-white border border-border rounded-lg p-6 text-center">
					<p class="text-gray-500 mb-0">No mends yet. Start your first memory mend!</p>
				</div>
			{:else if publicMends.length === 0}
				<div class="bg-white border border-border rounded-lg p-6 text-center">
					<p class="text-gray-500 mb-0">No public mends yet. Share a mend to see it here!</p>
				</div>
			{:else}
				<div class="grid grid-cols-2 md:grid-cols-3 gap-5">
					{#each publicMends as mend (mend.id)}
						<button
							class="flex flex-col items-start gap-2 cursor-pointer bg-transparent border-none p-0 text-left"
							onclick={() => goto(`/profile/mend/${mend.id}`)}
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

							<p class="text-xs text-gray-500 mb-0 uppercase font-mono">{formatDate(mend.createdAt)}</p>
						</button>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
