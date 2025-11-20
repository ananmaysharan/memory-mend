<script lang="ts">
	/**
	 * Editable bounding box component
	 * Allows users to drag corner vertices to adjust detection area
	 * Similar to document scanning in Apple Notes
	 */

	import type { Detection } from "$lib/types/mend";
	import BackButton from "../navigation/BackButton.svelte";
	import Button from "../ui/Button.svelte";

	interface Props {
		/** Base64 image to display */
		image: string;
		/** Initial detection (if any) */
		detection?: Detection | null;
		/** Callback when bounding box changes */
		onChange: (detection: Detection | null) => void;
	}

	let { image, detection = null, onChange }: Props = $props();

	// Component state
	let imageElement = $state<HTMLImageElement | null>(null);
	let containerElement = $state<HTMLDivElement | null>(null);
	let imageWidth = $state(0);
	let imageHeight = $state(0);
	let scale = $state(1);

	// Bounding box state (null if no box)
	let box = $state(detection ? { ...detection.boundingBox } : null);
	let confidence = $state(detection?.confidence || 0);

	// Dragging state
	let draggingVertex = $state<"tl" | "tr" | "bl" | "br" | null>(null);

	// Update box when detection prop changes
	$effect(() => {
		if (detection) {
			box = { ...detection.boundingBox };
			confidence = detection.confidence;
		}
	});

	// Calculate scale when image loads
	function handleImageLoad(event: Event) {
		const img = event.target as HTMLImageElement;
		imageWidth = img.naturalWidth;
		imageHeight = img.naturalHeight;

		const container = containerElement;
		if (!container) return;

		const containerWidth = container.clientWidth;
		const containerHeight = container.clientHeight;

		// Calculate scale to fit image in container
		scale = Math.min(
			containerWidth / imageWidth,
			containerHeight / imageHeight,
		);
	}

	// Add manual bounding box (centered, 50% of image size)
	function addManualBox() {
		const width = Math.floor(imageWidth * 0.5);
		const height = Math.floor(imageHeight * 0.5);
		const x = Math.floor((imageWidth - width) / 2);
		const y = Math.floor((imageHeight - height) / 2);

		box = { x, y, width, height };
		confidence = 1.0; // Manual boxes have 100% "confidence"

		onChange({
			boundingBox: { x, y, width, height },
			confidence: 1.0,
			className: "damage",
		});
	}

	// Remove bounding box
	function removeBox() {
		box = null;
		confidence = 0;
		onChange(null);
	}

	// Start dragging a vertex
	function startDrag(vertex: "tl" | "tr" | "bl" | "br") {
		draggingVertex = vertex;
	}

	// Handle mouse move during drag
	function handleMouseMove(event: MouseEvent) {
		if (!draggingVertex || !box || !imageElement || !containerElement)
			return;

		// Get mouse position relative to image
		const rect = imageElement.getBoundingClientRect();
		const mouseX = (event.clientX - rect.left) / scale;
		const mouseY = (event.clientY - rect.top) / scale;

		// Constrain to image bounds
		const clampedX = Math.max(0, Math.min(imageWidth, mouseX));
		const clampedY = Math.max(0, Math.min(imageHeight, mouseY));

		// Update bounding box based on which vertex is being dragged
		const newBox = { ...box };

		switch (draggingVertex) {
			case "tl": // Top-left
				newBox.width = box.x + box.width - clampedX;
				newBox.height = box.y + box.height - clampedY;
				newBox.x = clampedX;
				newBox.y = clampedY;
				break;

			case "tr": // Top-right
				newBox.width = clampedX - box.x;
				newBox.height = box.y + box.height - clampedY;
				newBox.y = clampedY;
				break;

			case "bl": // Bottom-left
				newBox.width = box.x + box.width - clampedX;
				newBox.height = clampedY - box.y;
				newBox.x = clampedX;
				break;

			case "br": // Bottom-right
				newBox.width = clampedX - box.x;
				newBox.height = clampedY - box.y;
				break;
		}

		// Ensure positive dimensions (minimum 20px)
		if (newBox.width > 20 && newBox.height > 20) {
			box = newBox;

			onChange({
				boundingBox: newBox,
				confidence,
				className: "damage",
			});
		}
	}

	// Stop dragging
	function stopDrag() {
		draggingVertex = null;
	}

	// Get vertex position in pixels
	function getVertexPosition(vertex: "tl" | "tr" | "bl" | "br") {
		if (!box) return { x: 0, y: 0 };

		switch (vertex) {
			case "tl":
				return { x: box.x * scale, y: box.y * scale };
			case "tr":
				return { x: (box.x + box.width) * scale, y: box.y * scale };
			case "bl":
				return { x: box.x * scale, y: (box.y + box.height) * scale };
			case "br":
				return {
					x: (box.x + box.width) * scale,
					y: (box.y + box.height) * scale,
				};
		}
	}
</script>

<svelte:window onmousemove={handleMouseMove} onmouseup={stopDrag} />

<div class="flex h-full flex-col gap-4">


	<!-- Image container with bounding box overlay -->
	<div
		bind:this={containerElement}
		class="relative flex-1 overflow-hidden rounded-lg bg-surface border border-gray-300"
		style="cursor: {draggingVertex ? 'grabbing' : 'default'};"
	>
		<!-- Image -->
		<img
			bind:this={imageElement}
			src={image}
			alt="Captured fabric"
			class="absolute inset-0 m-auto max-w-full max-h-full pointer-events-none select-none object-contain user-select-none -webkit-user-drag-none"
			onload={handleImageLoad}
			draggable="false"
		/>

		<!-- Bounding box overlay (only if box exists) -->
		{#if box && imageWidth > 0}
			<svg
				class="pointer-events-none absolute inset-0 m-auto"
				style="width: {imageWidth * scale}px; height: {imageHeight *
					scale}px; overflow: visible;"
			>
				<!-- Bounding box rectangle -->
				<rect
					x={box.x * scale}
					y={box.y * scale}
					width={box.width * scale}
					height={box.height * scale}
					fill="none"
					stroke="rgb(59, 130, 246)"
					stroke-width="3"
					stroke-dasharray="10 5"
					class="animate-pulse"
				/>

				<!-- Corner vertices (draggable) -->
				{#each ["tl", "tr", "bl", "br"] as vertex}
					{@const pos = getVertexPosition(
						vertex as "tl" | "tr" | "bl" | "br",
					)}
					<circle
						cx={pos.x}
						cy={pos.y}
						r="10"
						fill="white"
						stroke="rgb(59, 130, 246)"
						stroke-width="2"
						class="pointer-events-auto cursor-grab active:cursor-grabbing drop-shadow-md"
						style="cursor: {draggingVertex === vertex
							? 'grabbing'
							: 'grab'}; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));"
						onmousedown={() =>
							startDrag(vertex as "tl" | "tr" | "bl" | "br")}
					/>
				{/each}
			</svg>

			<!-- Confidence badge -->
			<!-- <div class="absolute left-4 top-4 rounded-lg bg-blue-500 px-3 py-1 text-sm font-medium text-white">
				{confidence < 1 ? `${Math.round(confidence * 100)}% confidence` : 'Manual selection'}
			</div> -->
		{/if}
	</div>

	<!-- Controls -->
	 	<div class="flex flex-col">
		<!-- Instructions -->
		<p class="flex-1 text-sm text-gray-600 self-center">
			{#if box}
				Drag the corner circles to adjust the detection area.
			{:else}
				No damage detected. Add a box manually to mark the repair area.
			{/if}
		</p>

		{#if box}
			<!-- Remove box button -->
			<Button onclick={removeBox}>Remove Box</Button>
		{:else}
			<!-- Add manual box button -->
			<Button onclick={addManualBox} disabled={imageWidth === 0}>
				Add Detection Box
			</Button>
		{/if}
	</div>
</div>

<style>
	/* Smooth transitions for box adjustments */
	rect {
		transition: stroke-dashoffset 0.5s linear;
	}

	/* Prevent text selection during drag */
	:global(body.dragging) {
		user-select: none;
		-webkit-user-select: none;
	}
</style>
