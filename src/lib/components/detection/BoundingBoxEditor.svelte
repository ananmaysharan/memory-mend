<script lang="ts">
	/**
	 * Editable bounding box component
	 * Allows users to drag corner vertices to adjust detection area
	 * Similar to document scanning in Apple Notes
	 */

	import type { Detection } from "$lib/types/mend";
	import BackButton from "../navigation/BackButton.svelte";
	import Button from "../ui/Button.svelte";
	import Plus from "phosphor-svelte/lib/Plus";
	import Trash from "phosphor-svelte/lib/Trash";


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
	let svgElement = $state<SVGSVGElement | null>(null);
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

	// Helper function to extract coordinates from mouse or touch events
	function getEventCoordinates(event: MouseEvent | TouchEvent): { clientX: number; clientY: number } {
		if (event instanceof MouseEvent) {
			return { clientX: event.clientX, clientY: event.clientY };
		} else if (event instanceof TouchEvent && event.touches.length > 0) {
			return { clientX: event.touches[0].clientX, clientY: event.touches[0].clientY };
		}
		// Fallback for touchend (use changedTouches)
		return { clientX: 0, clientY: 0 };
	}

	// Start dragging a vertex
	function startDrag(vertex: "tl" | "tr" | "bl" | "br", event: MouseEvent | TouchEvent) {
		event.stopPropagation();
		event.preventDefault();
		draggingVertex = vertex;
	}

	// Handle mouse/touch move during drag
	function handleMouseMove(event: MouseEvent | TouchEvent) {
		if (!draggingVertex || !box || !svgElement || !containerElement)
			return;

		event.preventDefault();

		// Get pointer position relative to SVG (where vertices are actually drawn)
		const coords = getEventCoordinates(event);
		const rect = svgElement.getBoundingClientRect();
		const mouseX = (coords.clientX - rect.left) / scale;
		const mouseY = (coords.clientY - rect.top) / scale;

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

<svelte:window
	onmousemove={handleMouseMove}
	onmouseup={stopDrag}
	ontouchmove={handleMouseMove}
	ontouchend={stopDrag}
/>

<div class="flex h-full flex-col">

	<!-- Image container wrapper with consistent padding -->
	<div class="flex-1 flex items-center justify-center p-4">
		<!-- Image container with bounding box overlay -->
		<div
			bind:this={containerElement}
			class="relative w-full max-w-md overflow-hidden rounded bg-surface"
			style="aspect-ratio: 3/4;"
		>
		<!-- Image -->
		<img
			bind:this={imageElement}
			src={image}
			alt="Captured fabric"
			class="w-full h-full object-contain pointer-events-none select-none user-select-none -webkit-user-drag-none"
			onload={handleImageLoad}
			draggable="false"
		/>

		<!-- Bounding box overlay (only if box exists) -->
		{#if box && imageWidth > 0}
			<svg
				bind:this={svgElement}
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
					stroke="var(--color-blue)"
					stroke-width="3"
					stroke-dasharray="10 5"
					class="animate-pulse"
				/>

				<!-- Corner vertices (draggable) -->
				{#each ["tl", "tr", "bl", "br"] as vertex (vertex)}
					{@const pos = getVertexPosition(
						vertex as "tl" | "tr" | "bl" | "br",
					)}
					<circle
						cx={pos.x}
						cy={pos.y}
						r="10"
						fill="white"
						stroke="var(--color-blue)"
						stroke-width="2"
						class="pointer-events-auto cursor-grab"
						role="button"
						tabindex="0"
						aria-label="Drag to adjust {vertex === 'tl' ? 'top-left' : vertex === 'tr' ? 'top-right' : vertex === 'bl' ? 'bottom-left' : 'bottom-right'} corner"
						onmousedown={(e) => startDrag(vertex as "tl" | "tr" | "bl" | "br", e)}
						ontouchstart={(e) => startDrag(vertex as "tl" | "tr" | "bl" | "br", e)}
					/>
				{/each}
			</svg>

			<!-- Confidence badge -->
			<!-- <div class="absolute left-4 top-4 rounded-lg bg-blue-500 px-3 py-1 text-sm font-medium text-white">
				{confidence < 1 ? `${Math.round(confidence * 100)}% confidence` : 'Manual selection'}
			</div> -->
		{/if}

		<!-- Overlay action buttons (top right) -->
		{#if box}
			<!-- Remove box button -->
			<button
				onclick={removeBox}
				class="absolute right-4 top-4 max-w-fit flex items-center gap-2 rounded bg-red-500 px-3 py-2 text-sm font-medium text-white hover:bg-red-600 transition-colors"
			>
				<Trash size={18} weight="bold" />
				Remove
			</button>
		{:else}
			<!-- Add manual box button -->
			<button
				onclick={addManualBox}
				disabled={imageWidth === 0}
				class="absolute right-4 top-4 max-w-fit flex items-center gap-2 border-orange-800 rounded bg-orange-600 px-3 py-2 text-sm font-medium text-white hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
			>
				<Plus size={18} weight="bold" />
				Add
			</button>
		{/if}
		</div>
	</div>

	<!-- Controls -->
	 	<div class="flex flex-col p-4">
		<!-- Instructions -->
		<p class="mb-0 text-sm text-gray-600 self-center">
			{#if box}
				Drag the corner circles to adjust the detection area.
			{:else}
				No damage detected. Add a box manually to mark the repair area.
			{/if}
		</p>

		{#if box}
			<!-- Remove box button -->
			<!-- <Button onclick={removeBox}>Remove Box</Button> -->
		{:else}
			<!-- Add manual box button -->
			<!-- <Button onclick={addManualBox} disabled={imageWidth === 0}>
				Add Detection Box
			</Button> -->
		{/if}
	</div>
</div>

<style>
	/* Prevent text selection during drag */
	:global(body) {
		user-select: none;
		-webkit-user-select: none;
	}
</style>
