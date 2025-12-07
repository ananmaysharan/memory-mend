<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import PatternEditor from '$lib/components/pattern/PatternEditor.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';

	const mendId = $derived($page.params.id ?? '');
	const mend = $derived(historyStore.getMendById(mendId));
	const from = $derived($page.url.searchParams.get('from'));

	// Helper to detect if a mend is scanned from global database
	const isScanned = $derived.by(() => {
		if (!mend) return false;

		// Explicit source field (for newly scanned mends)
		if (mend.source === 'scanned') return true;

		// Heuristic for old scanned mends: no image and isPublic flag
		// Supabase doesn't store garment images, so empty image + isPublic = scanned
		if (mend.isPublic && (!mend.image || mend.image === '')) return true;

		return false;
	});

	const memoryDate = $derived(
		mend?.memory.timestamp
			? new Date(mend.memory.timestamp).toLocaleDateString('en-US', {
					year: 'numeric',
					month: 'long',
					day: 'numeric'
			  })
			: ''
	);

	onMount(() => {
		if (!mend) {
			goto('/');
		}
	});

	function handleDelete() {
		if (confirm('Are you sure you want to delete this mend?')) {
			historyStore.deleteMend(mendId);
			handleBack();
		}
	}

	function handleBack() {
		if (from === 'library') {
			goto('/history');
		} else {
			goto('/');
		}
	}
</script>

{#if mend}
	<div class="page">
		<TopBar title="Memory Mend" showBackButton={true} backHandler={handleBack} />
		<div class="page-content">
			<!-- Header section with title, date, and garment info -->
			<div class="mb-6">
				<h1 class="text-3xl md:text-4xl mb-1 font-cooper capitalize">
					{mend.memory.title || 'Your Memory'}
				</h1>
				<p class="text-xl text-gray-600 font-cooper">{memoryDate}</p>
				{#if mend.garmentType || mend.material}
					<p class="text-lg text-gray-500 mt-2 font-mono uppercase">
						{#if mend.material && mend.garmentType}
							{mend.material} {mend.garmentType}
						{:else if mend.garmentType}
							{mend.garmentType}
						{:else if mend.material}
							{mend.material}
						{/if}
					</p>
				{/if}
			</div>

			<!-- Memory Text -->
			{#if mend.memory.text}
				<div class="bg-white border border-border rounded-lg p-4 mb-6">
					<p class="font-cooper text-base m-0 italic">"{mend.memory.text}"</p>
				</div>
			{/if}

			<!-- Memory Images -->
			{#if mend.memory.images && mend.memory.images.length > 0}
				<div class="grid grid-cols-3 md:grid-cols-5 gap-4 mb-6">
					{#each mend.memory.images as image}
						<div class="relative bg-white p-2 md:p-3 shadow-sm aspect-square">
							<img src={image} alt="Memory" class="w-full h-full object-cover" />
						</div>
					{/each}
				</div>
			{/if}

			<!-- Stitch Pattern -->
			<div class="bg-white border border-border rounded-lg p-6 mb-6">
				<PatternEditor pattern={mend.pattern} large={true} />
			</div>

			<!-- Repair Area -->
			{#if !isScanned && mend.image}
				<div class="mb-6">
					<h2 class="text-2xl font-semibold mb-4 font-cooper">Repair Area</h2>
					<img src={mend.image} alt="Repair area" class="w-full rounded-lg" />
				</div>
			{/if}

			<!-- Action Button -->
			<div class="flex flex-col gap-2.5">
				{#if isScanned}
					<Button onclick={() => goto('/')}>Back to Home</Button>
				{:else}
					<Button onclick={handleDelete}>Delete Mend</Button>
				{/if}
			</div>
		</div>
	</div>
{:else}
	<div class="page">
		<TopBar title="Memory Mend" showBackButton={true} backHandler={handleBack} />
		<div class="page-content">
			<p>Mend not found.</p>
		</div>
	</div>
{/if}
