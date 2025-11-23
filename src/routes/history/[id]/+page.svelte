<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import PatternEditor from '$lib/components/pattern/PatternEditor.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';

	const mendId = $derived($page.params.id);
	const mend = $derived(historyStore.getMendById(mendId));
	const from = $derived($page.url.searchParams.get('from'));

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

	function formatDate(timestamp: number): string {
		return new Date(timestamp).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

{#if mend}
	<div class="page">
		<TopBar title="Mend Details" showBackButton={true} backHandler={handleBack} />
		<div class="page-content">
			<p>
				Created {formatDate(mend.createdAt)}
				{#if mend.updatedAt !== mend.createdAt}
					• Updated {formatDate(mend.updatedAt)}
				{/if}
			</p>
			{#if mend.garmentType || mend.material}
				<p class="text-sm text-gray-600 capitalize">
					{#if mend.material && mend.garmentType}
						{mend.material} {mend.garmentType}
					{:else if mend.garmentType}
						{mend.garmentType}
					{:else if mend.material}
						{mend.material}
					{/if}
				</p>
			{/if}
			
			<div class="flex flex-col gap-5">
				<div>
				<h2>Memory</h2>
					{#if mend.memory.title}
						<h3>{mend.memory.title}</h3>
					{/if}
					{#if mend.memory.text}
						<p class="mb-0 italic">"{mend.memory.text}"</p>
					{/if}
					{#if mend.memory.images && mend.memory.images.length > 0}
						<div class="flex flex-wrap gap-2.5 mt-2.5">
							{#each mend.memory.images as image}
								<img src={image} alt="Memory" width="200" class="mb-2.5" />
							{/each}
						</div>
					{/if}
				</div>
				<div>
					<h2>Stitch Pattern</h2>
					<PatternEditor pattern={mend.pattern} />
				</div>
				<div>
					<h2>Repair Area</h2>
					<img src={mend.image} alt="Repair area" />
				</div>

				<div>
					<!-- <div class="mb-5">
						<p><strong>Memory ID:</strong></p>
						<p style="font-family: monospace; font-size: 12px; word-break: break-all;">{mend.memory.id}</p>
					</div> -->

					<!-- <h2>Status</h2>
					<p class="mb-5" style="text-transform: capitalize;">{mend.status}</p> -->

					<div class="flex flex-col gap-2.5">
						<Button onclick={handleDelete}>Delete Mend</Button>
						<Button onclick={handleBack}>Back</Button>
					</div>
				</div>
			</div>
		</div>
	</div>
{:else}
	<div class="page">
		<TopBar title="Mend Details" showBackButton={true} backHandler={handleBack} />
		<div class="page-content">
			<p>Mend not found.</p>
			<Button onclick={handleBack}>Back</Button>
		</div>
	</div>
{/if}
