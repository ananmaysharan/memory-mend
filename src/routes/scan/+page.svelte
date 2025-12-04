<script lang="ts">
	/**
	 * Scan Page - Camera capture for pattern detection
	 */

	import { goto } from '$app/navigation';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import CameraCapture from '$lib/components/camera/CameraCapture.svelte';
	import { blobToBase64 } from '$lib/utils/imageUtils';
	import UploadSimple from 'phosphor-svelte/lib/UploadSimple';
	import PencilSimple from 'phosphor-svelte/lib/PencilSimple';

	let fileInputElement: HTMLInputElement | null = $state(null);

	function handleCameraCapture(imageData: string) {
		// Navigate to analyzing page with image data
		goto('/scan/analyzing', { state: { image: imageData } });
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
				goto('/scan/analyzing', { state: { image: base64 } });
			} catch (err) {
				console.error('Error reading file:', err);
			}
		}
	}
</script>

<div class="page">
	<TopBar title="Scan Mend" showBackButton={true} backDestination="/" />

	<div class="page-content">
		<h2 class="mb-4">Scan Pattern</h2>
		<p class="text-gray-600 mb-6">
			Position your camera over the embroidered pattern.
		</p>

		<!-- Camera Capture -->
		<div class="mb-6">
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
