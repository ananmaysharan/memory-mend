<script lang="ts">
	interface Props {
		images: string[];
		maxVisible?: number;
	}

	let { images, maxVisible = 3 }: Props = $props();

	// Predefined angles for realistic stack effect
	const angles = [-8, -4, -2, 0, 2, 4, 6, 8];

	// Get visible images with their rotation angles
	const stackedImages = $derived(() => {
		const visibleCount = Math.min(maxVisible, images.length);
		const result = [];

		for (let i = 0; i < visibleCount; i++) {
			result.push({
				src: images[i],
				angle: angles[i % angles.length],
				zIndex: i
			});
		}

		return result;
	});
</script>

<div class="relative w-full aspect-square flex items-center justify-center">
	{#each stackedImages() as { src, angle, zIndex }, index (src + index)}
		<div
			class="absolute w-[85%] h-[85%] bg-white p-2 shadow-md stack-item"
			style="
				transform: rotate({angle}deg) translateY({index * 2}px);
				z-index: {zIndex};
			"
		>
			<img {src} alt="Memory {index + 1}" class="w-full h-full object-cover" />
		</div>
	{/each}
</div>
