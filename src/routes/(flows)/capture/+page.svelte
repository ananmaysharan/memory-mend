<script lang="ts">
	import { goto } from '$app/navigation';
	import CameraCapture from '$lib/components/camera/CameraCapture.svelte';
	import GarmentDetailsInput from '$lib/components/capture/GarmentDetailsInput.svelte';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import { mendStore } from '$lib/stores/mendStore.svelte';
	import { blobToBase64 } from '$lib/utils/imageUtils';

	let showCamera = $state(false);
	let garmentType = $state('');
	let material = $state('');
	let fabricConstruction = $state('');
	let fileInputElement: HTMLInputElement;

	function handleCaptureImage() {
		showCamera = true;
	}

	async function handleUploadImage() {
		fileInputElement?.click();
	}

	async function handleFileUpload(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];

		if (file) {
			try {
				const base64 = await blobToBase64(file);
				mendStore.setImage(base64, garmentType, material, fabricConstruction);
				goto('/scanning');
			} catch (err) {
				console.error('Error reading file:', err);
			}
		}
	}

	function handleCapture(imageData: string) {
		mendStore.setImage(imageData, garmentType, material, fabricConstruction);
		goto('/scanning');
	}
</script>

<div class="page">
	<TopBar title="New Mend" showBackButton={true} backDestination="/" />
	<div class="page-content flex-1 overflow-hidden flex flex-col">
		{#if showCamera}
			<CameraCapture onCapture={handleCapture} />
		{:else}
			<GarmentDetailsInput
				bind:garmentType
				bind:material
				bind:fabricConstruction
				onCaptureImage={handleCaptureImage}
				onUploadImage={handleUploadImage}
			/>
			<input
				bind:this={fileInputElement}
				type="file"
				accept="image/*,image/heic,image/heif"
				onchange={handleFileUpload}
				class="hidden"
			/>
		{/if}
	</div>
</div>
