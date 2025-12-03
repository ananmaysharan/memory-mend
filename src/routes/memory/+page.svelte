<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import type { Memory } from '$lib/types/mend';
	import Button from '$lib/components/ui/Button.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { mendStore } from '$lib/stores/mendStore.svelte';
	import { hashMemory } from '$lib/utils/hashUtils';
	import { blobToBase64, resizeImage, compressImage } from '$lib/utils/imageUtils';
	import PlusCircle from "phosphor-svelte/lib/PlusCircle";
	import X from "phosphor-svelte/lib/X";


	const MAX_IMAGES = 6;

	let memoryTitle = $state('Memory Title');
	let memoryText = $state('');
	let memoryImages = $state<string[]>([]);
	let isProcessing = $state(false);
	let isDragging = $state(false);
	let fileInput: HTMLInputElement;

	const currentDate = new Date().toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'long',
		day: 'numeric'
	});

	onMount(() => {
		if (!mendStore.image) {
			goto('/capture');
		}
	});

	async function handleImageUpload(event: Event) {
		const target = event.target as HTMLInputElement;
		const files = target.files;

		if (files) {
			await processFiles(files);
		}

		// Reset input
		if (target) {
			target.value = '';
		}
	}

	function removeImage(index: number) {
		memoryImages = memoryImages.filter((_, i) => i !== index);
	}

	function openFilePicker() {
		fileInput?.click();
	}

	async function processFiles(files: FileList) {
		const newImages: string[] = [];
		const remainingSlots = MAX_IMAGES - memoryImages.length;
		const filesToProcess = Math.min(files.length, remainingSlots);

		for (let i = 0; i < filesToProcess; i++) {
			const file = files[i];
			if (file.type.startsWith('image/')) {
				try {
					// Convert to base64
					let base64 = await blobToBase64(file);

					// Resize to max 1024px to reduce size
					base64 = await resizeImage(base64, 1024, 1024);

					// Compress to reduce file size further (quality 0.75)
					base64 = await compressImage(base64, 0.75);

					newImages.push(base64);
				} catch (err) {
					console.error('Error processing image:', err);
					alert('Failed to process one or more images. Please try again.');
				}
			}
		}

		if (newImages.length > 0) {
			memoryImages = [...memoryImages, ...newImages];
		}
	}

	function handleDragEnter(e: DragEvent) {
		e.preventDefault();
		isDragging = true;
	}

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
	}

	function handleDragLeave(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
	}

	async function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragging = false;

		const files = e.dataTransfer?.files;
		if (files && files.length > 0) {
			await processFiles(files);
		}
	}

	async function handleSubmit() {
		if (!memoryTitle && !memoryText && memoryImages.length === 0) {
			alert('Please add a title, text, or at least one image');
			return;
		}

		isProcessing = true;

		try {
			const id = await hashMemory({
				title: memoryTitle || undefined,
				text: memoryText || undefined,
				images: memoryImages.length > 0 ? memoryImages : undefined
			});

			const memory: Memory = {
				id,
				title: memoryTitle || undefined,
				text: memoryText || undefined,
				images: memoryImages.length > 0 ? memoryImages : undefined,
				timestamp: Date.now()
			};

			await mendStore.setMemory(memory);
			goto('/pattern');
		} catch (err) {
			console.error('Error processing memory:', err);
			alert('Error processing memory');
		} finally {
			isProcessing = false;
		}
	}

	const canAddMore = $derived(memoryImages.length < MAX_IMAGES);
	const canSubmit = $derived(
		(memoryTitle.length > 0 || memoryText.length > 0 || memoryImages.length > 0) && !isProcessing
	);
</script>

<div class="page">
	<TopBar title="Add Memory" showBackButton={true} backDestination="/detection" />
	<div class="page-content">
		<!-- Header section with captured image, title, and date -->
		<div class="flex gap-4 mb-6 items-start">
			{#if mendStore.image}
				<img src={mendStore.image} alt="Captured garment" class="w-[100px] h-[100px] object-cover rounded-lg shrink-0" />
			{/if}
			<div class="flex-1">
				<input
					type="text"
					bind:value={memoryTitle}
					class="w-full text-3xl md:text-4xl bg-transparent border border-border rounded px-2 py-1 outline-none focus:border-grey-800 transition-colors"
					placeholder="Your Memory"
					disabled={isProcessing}
				/>
				<p class="text-xl text-gray-600 ml-1 mt-2 font-cooper">{currentDate}</p>
			</div>
		</div>

		<!-- Message box -->
		<div class="bg-white border border-border rounded-lg p-4 mb-6">
			<textarea
				bind:value={memoryText}
				placeholder="..."
				rows="6"
				class="w-full border-none bg-transparent font-cooper text-base resize-y outline-none"
				disabled={isProcessing}
			></textarea>
		</div>

		<!-- Image upload grid -->
		<div class="mb-6">
			{#if memoryImages.length === 0}
				<div
					class="bg-surface border-2 border-dashed border-border rounded-lg p-12 text-center cursor-pointer transition-all duration-200 hover:border-grey hover:bg-off-white"
					class:border-green={isDragging}
					class:bg-white={isDragging}
					role="button"
					tabindex="0"
					onclick={openFilePicker}
					ondragenter={handleDragEnter}
					ondragover={handleDragOver}
					ondragleave={handleDragLeave}
					ondrop={handleDrop}
				>
					<PlusCircle size={48} class="mx-auto mb-2 text-gray-400" />
					<p class="font-mono uppercase text-gray-400 m-0">Add Memory Media</p>
				</div>
			{:else}
				<div class="grid grid-cols-3 md:grid-cols-5 gap-4">
					{#each memoryImages as image, index}
						<div class="relative bg-white p-2 md:p-3 shadow-sm aspect-square">
							<img src={image} alt="Memory {index + 1}" class="w-full h-full object-cover" />
							<div
								role="button"
								class="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-white border-2 border-white cursor-pointer flex items-center justify-center transition-all duration-200 hover:scale-105 shadow-sm"
								onclick={() => removeImage(index)}
								aria-label="Remove image"
							>
							<X size={16} class="text-gray-600" weight="bold"/>
							</div>
						</div>
					{/each}
					{#if canAddMore}
						<div
							class="relative flex flex-col bg-surface border-2 border-dashed border-border rounded cursor-pointer flex items-center justify-center transition-all duration-200 hover:border-grey hover:bg-off-white aspect-square"
							role="button"
							tabindex="0"
							onclick={openFilePicker}
						>
							<PlusCircle size={48} class="mx-auto mb-2 text-gray-400" />
							<p class="font-mono uppercase text-gray-400 m-0 text-sm">Add More</p>
						</div>
					{/if}
				</div>
			{/if}
		</div>

		<!-- Hidden file input -->
		<input
			type="file"
			accept="image/*"
			multiple
			bind:this={fileInput}
			onchange={handleImageUpload}
			disabled={isProcessing || !canAddMore}
			class="hidden"
		/>

		<!-- Submit button -->
		<Button disabled={!canSubmit} onclick={handleSubmit}>
			{isProcessing ? 'Processing...' : 'Generate Encoded Pattern'}
		</Button>
	</div>
</div>
