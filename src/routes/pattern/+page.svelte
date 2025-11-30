<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import PatternEditor from '$lib/components/pattern/PatternEditor.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { mendStore } from '$lib/stores/mendStore.svelte';
	import { downloadPatternSVG } from '$lib/services/svgGenerator';

	const memoryDate = $derived(
		mendStore.memory?.timestamp
			? new Date(mendStore.memory.timestamp).toLocaleDateString('en-US', {
					year: 'numeric',
					month: 'long',
					day: 'numeric'
			  })
			: ''
	);

	onMount(() => {
		if (!mendStore.pattern || !mendStore.memory) {
			goto('/capture');
		}
	});

	function handleContinue() {
		mendStore.goToPreview();
		goto('/preview');
	}

	function handleDownloadSVG() {
		if (mendStore.pattern) {
			downloadPatternSVG(mendStore.pattern, 28); // Large cell size
		}
	}

	function goBack() {
		goto('/memory');
	}
</script>

<div class="page">
	<TopBar title="Your Pattern" showBackButton={true} backDestination="/memory" />
	<div class="page-content">
		<!-- Header section with captured image, title, and date -->
		<div class="flex gap-4 mb-6 items-start">
			<div class="flex-1">
				<h1 class="text-3xl font-cooper capitalize md:text-4xl mb-1">
					{mendStore.memory?.title || 'Your Memory'}
				</h1>
				<p class="text-xl text-gray-600 font-cooper">{memoryDate}</p>
			</div>
		</div>

		<!-- Pattern Display Section -->
		<div class="bg-white border border-border rounded-lg p-6 mb-6">
			{#if mendStore.pattern}
				<PatternEditor pattern={mendStore.pattern} large={true} />
			{:else}
				<p>No pattern available</p>
			{/if}
		</div>

		<!-- Memory Details Section -->
		{#if mendStore.memory?.text || (mendStore.memory?.images && mendStore.memory.images.length > 0)}
			<div class="mb-6">
				<!-- Memory Text -->
				{#if mendStore.memory?.text}
					<div class="bg-white border border-border rounded-lg p-4 mb-6">
						<p class="font-cooper text-base m-0 italic">"{mendStore.memory.text}"</p>
					</div>
				{/if}

				<!-- Memory Images -->
				{#if mendStore.memory?.images && mendStore.memory.images.length > 0}
					<div class="grid grid-cols-3 md:grid-cols-5 gap-4">
						{#each mendStore.memory.images as image, index}
							<div class="relative bg-white p-2 md:p-3 shadow-sm aspect-square">
								<img
									src={image}
									alt="Memory {index + 1}"
									class="w-full h-full object-cover"
								/>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}

		<!-- Action Buttons -->
		<div class="flex flex-col gap-2.5">
			<Button onclick={handleDownloadSVG}>Download SVG</Button>
			<Button onclick={handleContinue}>Proceed</Button>
		</div>
	</div>
</div>
