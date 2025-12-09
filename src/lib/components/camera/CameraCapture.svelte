<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { blobToBase64 } from '$lib/utils/imageUtils';
	import ArrowRight from "phosphor-svelte/lib/ArrowRight";
	import ArrowClockwise from "phosphor-svelte/lib/ArrowClockwise";


	interface Props {
		onCapture: (imageData: string) => void;
		showGridOverlay?: boolean;
	}

	let { onCapture, showGridOverlay = false }: Props = $props();

	let videoElement: HTMLVideoElement | null = $state(null);
	let canvasElement: HTMLCanvasElement | null = $state(null);
	let stream: MediaStream | null = $state(null);
	let isStreaming = $state(false);
	let error = $state<string | null>(null);
	let capturedImage = $state<string | null>(null);
	let torchSupported = $state(false);
	let torchEnabled = $state(false);

	// Grid overlay constants (matching ManualPatternInput)
	const GRID_SIZE = 7;
	const CELL_SIZE = 28;
	const gap = CELL_SIZE * 0.15;

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
				await enableTorch();
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
		torchEnabled = false;
		torchSupported = false;
	}

	async function enableTorch() {
		if (!stream) return;

		try {
			const videoTrack = stream.getVideoTracks()[0];

			// Check if getCapabilities is supported
			if (typeof videoTrack.getCapabilities !== 'function') {
				return;
			}

			const capabilities = videoTrack.getCapabilities();

			// Check if torch is supported
			if ('torch' in capabilities && capabilities.torch) {
				await videoTrack.applyConstraints({
					advanced: [{ torch: true } as any]
				});
				torchSupported = true;
				torchEnabled = true;
			}
		} catch (err) {
			console.warn('Could not enable torch:', err);
			torchSupported = false;
			torchEnabled = false;
		}
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
			<div class="flex-1 flex items-center justify-center">
				<div class="relative w-full max-w-md" style="aspect-ratio: 3/4;">
					<img
						src={capturedImage}
						alt="Captured"
						class="w-full h-full object-cover rounded"
					/>

					{#if showGridOverlay}
						<div class="absolute inset-0 flex items-center justify-center pointer-events-none" style="opacity: 0.5;">
							<div class="inline-flex flex-col relative">
								<!-- Top row: TL fiducial, empty cells, TR fiducial -->
								<div class="flex">
									<!-- TL Fiducial: X -->
									<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;">
										<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
											<line
												x1={CELL_SIZE * 0.1}
												y1={CELL_SIZE * 0.1}
												x2={CELL_SIZE * 0.9}
												y2={CELL_SIZE * 0.9}
												stroke="#fff"
												stroke-width={CELL_SIZE * 0.12}
												stroke-linecap="butt"
											/>
											<line
												x1={CELL_SIZE * 0.9}
												y1={CELL_SIZE * 0.1}
												x2={CELL_SIZE * 0.1}
												y2={CELL_SIZE * 0.9}
												stroke="#fff"
												stroke-width={CELL_SIZE * 0.12}
												stroke-linecap="butt"
											/>
										</svg>
									</div>
									{#each Array(GRID_SIZE) as _}
										<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"></div>
									{/each}
									<!-- TR Fiducial: || -->
									<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;">
										<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
											<line
												x1={CELL_SIZE * 0.35}
												y1={CELL_SIZE * 0.1}
												x2={CELL_SIZE * 0.35}
												y2={CELL_SIZE * 0.9}
												stroke="#fff"
												stroke-width={CELL_SIZE * 0.12}
												stroke-linecap="butt"
											/>
											<line
												x1={CELL_SIZE * 0.65}
												y1={CELL_SIZE * 0.1}
												x2={CELL_SIZE * 0.65}
												y2={CELL_SIZE * 0.9}
												stroke="#fff"
												stroke-width={CELL_SIZE * 0.12}
												stroke-linecap="butt"
											/>
										</svg>
									</div>
								</div>

								<!-- Middle rows: empty cell, 7x7 data grid, empty cell -->
								{#each Array(GRID_SIZE) as _, rowIndex}
									<div class="flex">
										<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"></div>
										{#each Array(GRID_SIZE) as _, colIndex}
											<div
												class="border border-white box-border"
												style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"
											></div>
										{/each}
										<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"></div>
									</div>
								{/each}

								<!-- Bottom row: BL fiducial, empty cells, BR fiducial -->
								<div class="flex">
									<!-- BL Fiducial: O -->
									<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;">
										<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
											<circle
												cx={CELL_SIZE / 2}
												cy={CELL_SIZE / 2}
												r={(CELL_SIZE - CELL_SIZE * 0.24) / 2}
												fill="none"
												stroke="#fff"
												stroke-width={CELL_SIZE * 0.12}
											/>
										</svg>
									</div>
									{#each Array(GRID_SIZE) as _}
										<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"></div>
									{/each}
									<!-- BR Fiducial: ■ -->
									<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;">
										<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
											<rect
												x={CELL_SIZE * 0.1}
												y={CELL_SIZE * 0.1}
												width={CELL_SIZE * 0.8}
												height={CELL_SIZE * 0.8}
												fill="none"
												stroke="#fff"
												stroke-width={CELL_SIZE * 0.12}
											/>
										</svg>
									</div>
								</div>

								<!-- Border lines connecting fiducials -->
								<svg
									class="absolute top-0 left-0 pointer-events-none"
									width={(GRID_SIZE + 2) * CELL_SIZE}
									height={(GRID_SIZE + 2) * CELL_SIZE}
									xmlns="http://www.w3.org/2000/svg"
								>
									<!-- Top line: X to || -->
									<line
										x1={CELL_SIZE * 0.9 + gap}
										y1={CELL_SIZE * 0.5}
										x2={8 * CELL_SIZE + CELL_SIZE * 0.35 - gap}
										y2={CELL_SIZE * 0.5}
										stroke="#fff"
										stroke-width={CELL_SIZE * 0.12}
										stroke-linecap="butt"
									/>
									<!-- Right line: || to ■ -->
									<line
										x1={8 * CELL_SIZE + CELL_SIZE * 0.5}
										y1={CELL_SIZE * 0.9 + gap}
										x2={8 * CELL_SIZE + CELL_SIZE * 0.5}
										y2={8 * CELL_SIZE + CELL_SIZE * 0.1 - gap}
										stroke="#fff"
										stroke-width={CELL_SIZE * 0.12}
										stroke-linecap="butt"
									/>
									<!-- Bottom line: O to ■ -->
									<line
										x1={CELL_SIZE * 0.88 + gap}
										y1={8 * CELL_SIZE + CELL_SIZE * 0.5}
										x2={8 * CELL_SIZE + CELL_SIZE * 0.1 - gap}
										y2={8 * CELL_SIZE + CELL_SIZE * 0.5}
										stroke="#fff"
										stroke-width={CELL_SIZE * 0.12}
										stroke-linecap="butt"
									/>
									<!-- Left line: X to O -->
									<line
										x1={CELL_SIZE * 0.5}
										y1={CELL_SIZE * 0.9 + gap}
										x2={CELL_SIZE * 0.5}
										y2={8 * CELL_SIZE + CELL_SIZE * 0.12 - gap}
										stroke="#fff"
										stroke-width={CELL_SIZE * 0.12}
										stroke-linecap="butt"
									/>
								</svg>
							</div>
						</div>
					{/if}
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

					{#if showGridOverlay}
						<div class="absolute inset-0 flex items-center justify-center pointer-events-none" style="opacity: 0.5;">
							<div class="inline-flex flex-col relative">
								<!-- Top row: TL fiducial, empty cells, TR fiducial -->
								<div class="flex">
									<!-- TL Fiducial: X -->
									<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;">
										<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
											<line
												x1={CELL_SIZE * 0.1}
												y1={CELL_SIZE * 0.1}
												x2={CELL_SIZE * 0.9}
												y2={CELL_SIZE * 0.9}
												stroke="#fff"
												stroke-width={CELL_SIZE * 0.12}
												stroke-linecap="butt"
											/>
											<line
												x1={CELL_SIZE * 0.9}
												y1={CELL_SIZE * 0.1}
												x2={CELL_SIZE * 0.1}
												y2={CELL_SIZE * 0.9}
												stroke="#fff"
												stroke-width={CELL_SIZE * 0.12}
												stroke-linecap="butt"
											/>
										</svg>
									</div>
									{#each Array(GRID_SIZE) as _}
										<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"></div>
									{/each}
									<!-- TR Fiducial: || -->
									<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;">
										<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
											<line
												x1={CELL_SIZE * 0.35}
												y1={CELL_SIZE * 0.1}
												x2={CELL_SIZE * 0.35}
												y2={CELL_SIZE * 0.9}
												stroke="#fff"
												stroke-width={CELL_SIZE * 0.12}
												stroke-linecap="butt"
											/>
											<line
												x1={CELL_SIZE * 0.65}
												y1={CELL_SIZE * 0.1}
												x2={CELL_SIZE * 0.65}
												y2={CELL_SIZE * 0.9}
												stroke="#fff"
												stroke-width={CELL_SIZE * 0.12}
												stroke-linecap="butt"
											/>
										</svg>
									</div>
								</div>

								<!-- Middle rows: empty cell, 7x7 data grid, empty cell -->
								{#each Array(GRID_SIZE) as _, rowIndex}
									<div class="flex">
										<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"></div>
										{#each Array(GRID_SIZE) as _, colIndex}
											<div
												class="border border-white box-border"
												style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"
											></div>
										{/each}
										<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"></div>
									</div>
								{/each}

								<!-- Bottom row: BL fiducial, empty cells, BR fiducial -->
								<div class="flex">
									<!-- BL Fiducial: O -->
									<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;">
										<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
											<circle
												cx={CELL_SIZE / 2}
												cy={CELL_SIZE / 2}
												r={(CELL_SIZE - CELL_SIZE * 0.24) / 2}
												fill="none"
												stroke="#fff"
												stroke-width={CELL_SIZE * 0.12}
											/>
										</svg>
									</div>
									{#each Array(GRID_SIZE) as _}
										<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;"></div>
									{/each}
									<!-- BR Fiducial: ■ -->
									<div class="box-border" style="width: {CELL_SIZE}px; height: {CELL_SIZE}px;">
										<svg width={CELL_SIZE} height={CELL_SIZE} xmlns="http://www.w3.org/2000/svg">
											<rect
												x={CELL_SIZE * 0.1}
												y={CELL_SIZE * 0.1}
												width={CELL_SIZE * 0.8}
												height={CELL_SIZE * 0.8}
												fill="none"
												stroke="#fff"
												stroke-width={CELL_SIZE * 0.12}
											/>
										</svg>
									</div>
								</div>

								<!-- Border lines connecting fiducials -->
								<svg
									class="absolute top-0 left-0 pointer-events-none"
									width={(GRID_SIZE + 2) * CELL_SIZE}
									height={(GRID_SIZE + 2) * CELL_SIZE}
									xmlns="http://www.w3.org/2000/svg"
								>
									<!-- Top line: X to || -->
									<line
										x1={CELL_SIZE * 0.9 + gap}
										y1={CELL_SIZE * 0.5}
										x2={8 * CELL_SIZE + CELL_SIZE * 0.35 - gap}
										y2={CELL_SIZE * 0.5}
										stroke="#fff"
										stroke-width={CELL_SIZE * 0.12}
										stroke-linecap="butt"
									/>
									<!-- Right line: || to ■ -->
									<line
										x1={8 * CELL_SIZE + CELL_SIZE * 0.5}
										y1={CELL_SIZE * 0.9 + gap}
										x2={8 * CELL_SIZE + CELL_SIZE * 0.5}
										y2={8 * CELL_SIZE + CELL_SIZE * 0.1 - gap}
										stroke="#fff"
										stroke-width={CELL_SIZE * 0.12}
										stroke-linecap="butt"
									/>
									<!-- Bottom line: O to ■ -->
									<line
										x1={CELL_SIZE * 0.88 + gap}
										y1={8 * CELL_SIZE + CELL_SIZE * 0.5}
										x2={8 * CELL_SIZE + CELL_SIZE * 0.1 - gap}
										y2={8 * CELL_SIZE + CELL_SIZE * 0.5}
										stroke="#fff"
										stroke-width={CELL_SIZE * 0.12}
										stroke-linecap="butt"
									/>
									<!-- Left line: X to O -->
									<line
										x1={CELL_SIZE * 0.5}
										y1={CELL_SIZE * 0.9 + gap}
										x2={CELL_SIZE * 0.5}
										y2={8 * CELL_SIZE + CELL_SIZE * 0.12 - gap}
										stroke="#fff"
										stroke-width={CELL_SIZE * 0.12}
										stroke-linecap="butt"
									/>
								</svg>
							</div>
						</div>
					{/if}
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
