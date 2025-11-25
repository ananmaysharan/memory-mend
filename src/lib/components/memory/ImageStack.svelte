<script lang="ts">
	interface Props {
		images: string[];
		maxVisible?: number;
	}

	let { images, maxVisible = 3 }: Props = $props();

	let currentIndex = $state(0);
	let touchStartX = $state(0);
	let touchEndX = $state(0);

	// Predefined angles for realistic stack effect
	const angles = [-8, -4, -2, 0, 2, 4, 6, 8];

	// Get visible images with their rotation angles
	const stackedImages = $derived(() => {
		const visibleCount = Math.min(maxVisible, images.length);
		const result = [];

		for (let i = 0; i < visibleCount; i++) {
			const imageIndex = (currentIndex + i) % images.length;
			result.push({
				src: images[imageIndex],
				angle: angles[i % angles.length],
				zIndex: i
			});
		}

		return result;
	});

	function cycleNext() {
		currentIndex = (currentIndex + 1) % images.length;
	}

	function handleTouchStart(e: TouchEvent) {
		touchStartX = e.touches[0].clientX;
	}

	function handleTouchMove(e: TouchEvent) {
		touchEndX = e.touches[0].clientX;
	}

	function handleTouchEnd() {
		const swipeDistance = touchStartX - touchEndX;
		const minSwipeDistance = 50;

		if (Math.abs(swipeDistance) > minSwipeDistance) {
			if (swipeDistance > 0) {
				// Swiped left - go to next
				cycleNext();
			} else {
				// Swiped right - go to previous
				currentIndex = (currentIndex - 1 + images.length) % images.length;
			}
		}
	}

	function handleClick(e: MouseEvent) {
		// Cycle to next image on click
		e.stopPropagation();
		cycleNext();
	}
</script>

<div
	class="relative w-full aspect-square flex items-center justify-center cursor-pointer select-none"
	role="button"
	tabindex="0"
	onclick={handleClick}
	ontouchstart={handleTouchStart}
	ontouchmove={handleTouchMove}
	ontouchend={handleTouchEnd}
	onkeydown={(e) => {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			cycleNext();
		}
	}}
>
	{#each stackedImages() as { src, angle, zIndex }, index (src + index)}
		<div
			class="absolute w-[85%] h-[85%] bg-white p-2 shadow-md transition-transform duration-300 ease-in-out pointer-events-none stack-item"
			style="
				transform: rotate({angle}deg) translateY({index * 2}px);
				z-index: {zIndex};
			"
		>
			<img {src} alt="Memory {index + 1}" class="w-full h-full object-cover pointer-events-none" />
		</div>
	{/each}
</div>

<style>
	:global(.relative.w-full.aspect-square:hover) .stack-item {
		transform: rotate(0deg) translateY(0px) !important;
	}
</style>
