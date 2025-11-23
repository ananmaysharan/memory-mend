<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { blobToBase64 } from '$lib/utils/imageUtils';
	import ArrowRight from "phosphor-svelte/lib/ArrowRight";
	import ArrowClockwise from "phosphor-svelte/lib/ArrowClockwise";


	interface Props {
		onCapture: (imageData: string) => void;
	}

	let { onCapture }: Props = $props();

	let videoElement: HTMLVideoElement | null = $state(null);
	let canvasElement: HTMLCanvasElement | null = $state(null);
	let stream: MediaStream | null = $state(null);
	let isStreaming = $state(false);
	let error = $state<string | null>(null);
	let capturedImage = $state<string | null>(null);

	async function startCamera() {
		try {
			error = null;
			// Use back camera on mobile (environment), fallback to any camera
			const mediaStream = await navigator.mediaDevices.getUserMedia({
				video: {
					facingMode: 'environment', // Back camera on mobile
					aspectRatio: 3/4 // Request 3:4 aspect ratio (vertical)
				},
				audio: false
			});

			stream = mediaStream;

			if (videoElement) {
				videoElement.srcObject = mediaStream;
				await videoElement.play();
				isStreaming = true;
			}
		} catch (err) {
			console.error('Error accessing camera:', err);
			error = 'Could not access camera';
		}
	}

	function stopCamera() {
		if (stream) {
			stream.getTracks().forEach((track) => track.stop());
			stream = null;
		}
		isStreaming = false;
	}

	function capturePhoto() {
		if (!videoElement || !canvasElement) return;

		const context = canvasElement.getContext('2d');
		if (!context) return;

		const sourceWidth = videoElement.videoWidth;
		const sourceHeight = videoElement.videoHeight;
		const targetRatio = 3 / 4;

		// Calculate dimensions to maintain 3:4 aspect ratio (vertical)
		let captureWidth = sourceWidth;
		let captureHeight = sourceHeight;
		let offsetX = 0;
		let offsetY = 0;

		const sourceRatio = sourceWidth / sourceHeight;

		if (sourceRatio > targetRatio) {
			// Source is wider - crop width (center crop)
			captureWidth = sourceHeight * targetRatio;
			offsetX = (sourceWidth - captureWidth) / 2;
		} else if (sourceRatio < targetRatio) {
			// Source is taller - crop height (center crop)
			captureHeight = sourceWidth / targetRatio;
			offsetY = (sourceHeight - captureHeight) / 2;
		}

		canvasElement.width = captureWidth;
		canvasElement.height = captureHeight;

		// Draw the cropped portion centered
		context.drawImage(
			videoElement,
			offsetX,
			offsetY,
			captureWidth,
			captureHeight,
			0,
			0,
			captureWidth,
			captureHeight
		);

		const imageData = canvasElement.toDataURL('image/jpeg', 0.9);
		capturedImage = imageData;
		stopCamera();
	}

	function retake() {
		capturedImage = null;
		startCamera();
	}

	function confirmPhoto() {
		if (capturedImage) {
			onCapture(capturedImage);
		}
	}

	async function handleFileUpload(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];

		if (file) {
			try {
				const base64 = await blobToBase64(file);
				capturedImage = base64;
				stopCamera();
			} catch (err) {
				console.error('Error reading file:', err);
				error = 'Could not read image file';
			}
		}
	}

	onMount(() => {
		startCamera();
		return () => stopCamera();
	});
</script>

<div class="w-full h-full flex flex-col">
	{#if error}
		<div class="p-4">
			<p class="mb-5">{error}</p>
			<label
				for="file-upload"
				class="block py-2.5 px-5 text-center bg-orange-600 text-white cursor-pointer text-sm font-medium uppercase border border-orange-800 hover:bg-orange-700 font-mono"
			>
				<span>Upload image instead</span>
			</label>
			<input
				id="file-upload"
				type="file"
				accept="image/*"
				onchange={handleFileUpload}
				class="hidden"
			/>
		</div>
	{:else if capturedImage}
		<div class="flex flex-col h-full w-full">
			<div class="flex-1 flex items-center justify-center p-4">
				<div class="w-full max-w-md" style="aspect-ratio: 3/4;">
					<img
						src={capturedImage}
						alt="Captured"
						class="w-full h-full object-cover rounded"
					/>
				</div>
			</div>
			<div class="flex flex-row gap-2.5 p-4 bg-[--color-surface]">
				<Button onclick={retake}><ArrowClockwise size={18} weight="bold" />Retake</Button>
				<Button onclick={confirmPhoto}>Use Photo<ArrowRight size={18} weight="bold" /></Button>

			</div>
		</div>
	{:else}
		<div class="flex flex-col h-full w-full">
			<div class="relative w-full flex-1 flex items-center justify-center p-4">
				<div class="relative w-full max-w-md" style="aspect-ratio: 3/4;">
					<video
						bind:this={videoElement}
						autoplay
						playsinline
						muted
						class="absolute inset-0 w-full h-full object-cover rounded bg-surface"
					></video>
				</div>
			</div>
			<canvas bind:this={canvasElement} class="hidden"></canvas>

			{#if isStreaming}
				<div class="flex flex-col gap-2.5 p-4 bg-[--color-surface]">
					<Button onclick={capturePhoto}>Capture</Button>
				</div>
			{/if}
		</div>
	{/if}
</div>
