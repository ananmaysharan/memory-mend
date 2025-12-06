<script lang="ts">
	/**
	 * Scan Page - Camera capture for pattern detection
	 */

	import { goto } from '$app/navigation';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import CameraCapture from '$lib/components/camera/CameraCapture.svelte';
	import { blobToBase64 } from '$lib/utils/imageUtils';
	import { scanStore } from '$lib/stores/scanStore.svelte';
	import UploadSimple from 'phosphor-svelte/lib/UploadSimple';
	import PencilSimple from 'phosphor-svelte/lib/PencilSimple';

	let fileInputElement: HTMLInputElement | null = $state(null);

	function handleCameraCapture(imageData: string) {
		// Store image in scan store and navigate to analyzing page
		scanStore.setScannedImage(imageData);
		goto('/scan/analyzing');
	}

	function handleManualDecode() {
		goto('/scan/manual');
	}

	function handleUploadClick() {
		fileInputElement?.click();
	}

	async function handleFileUpload(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];

		if (file) {
			try {
				const base64 = await blobToBase64(file);
				// Store image in scan store and navigate to analyzing page
				scanStore.setScannedImage(base64);
				goto('/scan/analyzing');
			} catch (err) {
				console.error('Error reading file:', err);
			}
		}
	}
</script>

<div class="page">
	<TopBar title="Scan Mend" showBackButton={true} backDestination="/" />

	<div class="page-content">

		<!-- Camera Capture -->
		<div class="mb-6 flex flex-col gap-2.5">
			<CameraCapture onCapture={handleCameraCapture} />
		</div>

		<!-- Alternative options -->
		<div class="flex flex-col gap-2.5">
			<button
				onclick={handleUploadClick}
			>
				<UploadSimple size={18} weight="bold" />
				Upload Image
			</button>
			<p class="text-center italic">or...</p>
			<button
				onclick={handleManualDecode}
			>
				<PencilSimple size={18} weight="bold" />
				Decode Manually
			</button>
		</div>

		<!-- Hidden file input -->
		<input
			bind:this={fileInputElement}
			type="file"
			accept="image/*"
			onchange={handleFileUpload}
			class="hidden"
		/>
	</div>
</div>
