<script lang="ts">
	import type { Memory } from '$lib/types/mend';
	import Button from '$lib/components/ui/Button.svelte';
	import { hashMemory } from '$lib/utils/hashUtils';
	import { blobToBase64 } from '$lib/utils/imageUtils';

	interface Props {
		onSubmit: (memory: Memory) => void;
	}

	let { onSubmit }: Props = $props();

	let memoryText = $state('');
	let memoryImage = $state<string | null>(null);
	let isProcessing = $state(false);

	async function handleImageUpload(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];

		if (file) {
			try {
				const base64 = await blobToBase64(file);
				memoryImage = base64;
			} catch (err) {
				console.error('Error reading image:', err);
			}
		}
	}

	function removeImage() {
		memoryImage = null;
	}

	async function handleSubmit() {
		if (!memoryText && !memoryImage) {
			alert('Please enter a memory or upload an image');
			return;
		}

		isProcessing = true;

		try {
			const id = await hashMemory({
				text: memoryText || undefined,
				image: memoryImage || undefined
			});

			const memory: Memory = {
				id,
				text: memoryText || undefined,
				image: memoryImage || undefined,
				timestamp: Date.now()
			};

			onSubmit(memory);
		} catch (err) {
			console.error('Error processing memory:', err);
			alert('Error processing memory');
		} finally {
			isProcessing = false;
		}
	}

	const canSubmit = $derived((memoryText.length > 0 || memoryImage !== null) && !isProcessing);
</script>

<div>
	<div class="mb-5">
		<label for="memory-text">Enter your memory:</label>
		<textarea
			id="memory-text"
			bind:value={memoryText}
			placeholder="..."
			rows="6"
			disabled={isProcessing}
		></textarea>
	</div>

	<div class="mb-5">
		<label>Add a Photo</label>

		{#if memoryImage}
			<div class="flex flex-col gap-2.5">
				<img src={memoryImage} alt="Memory"/>
				<Button onclick={removeImage}>Remove</Button>
			</div>
		{:else}
			<input type="file" accept="image/*" onchange={handleImageUpload} disabled={isProcessing} />
		{/if}
	</div>

	<Button disabled={!canSubmit} onclick={handleSubmit}>
		{isProcessing ? 'Processing...' : 'Generate Pattern'}
	</Button>
</div>
