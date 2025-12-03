<script lang="ts">
	/**
	 * Scanning page - Shows animated scanning bar while damage detection runs
	 * Provides visual feedback during the detection process
	 */

	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { mendStore } from '$lib/stores/mendStore.svelte';
	import { detectDamage } from '$lib/services/imageProcessing';
	import type { Detection } from '$lib/types/mend';
	import TopBar from '$lib/components/navigation/TopBar.svelte';

	// Component state
	let scanCount = $state(0);
	let detectionComplete = $state(false);
	let detectionResult = $state<Detection | null>(null);
	let error = $state<string | null>(null);
	const MIN_SCANS = 2;
	const SCAN_DURATION = 2000; // 2 seconds per cycle

	onMount(async () => {
		// Redirect if no image
		if (!mendStore.image) {
			await goto('/capture');
			return;
		}

		// Start detection immediately
		detectDamage(mendStore.image)
			.then((result) => {
				detectionResult = result;
				detectionComplete = true;
				checkAndProceed();
			})
			.catch((err) => {
				console.error('Detection error:', err);
				error = err instanceof Error ? err.message : 'Failed to detect damage';
				detectionComplete = true;
				checkAndProceed();
			});

		// Track scan cycles (counts completed cycles)
		const scanInterval = setInterval(() => {
			scanCount++;
			if (scanCount >= MIN_SCANS) {
				clearInterval(scanInterval);
				checkAndProceed();
			}
		}, SCAN_DURATION);
	});

	function checkAndProceed() {
		if (scanCount >= MIN_SCANS && detectionComplete) {
			// Store detection result (or null if failed) along with any error
			mendStore.setDetection(detectionResult, error);

			// Navigate to detection page (will show error there if detection failed)
			goto('/detection');
		}
	}
</script>

<div class="page h-screen">
	<!-- Top bar without back button to prevent interruption -->
	<TopBar title="Analyzing Damage" showBackButton={false} />

	<!-- Main content -->
	<main class="page-content flex-1 overflow-hidden flex flex-col">
		<!-- Image container matching BoundingBoxEditor positioning -->
		<div class="flex-1 flex items-center justify-center p-4">
			<div
				class="relative w-full max-w-md overflow-hidden rounded bg-surface"
				style="aspect-ratio: 3/4;"
			>
				<!-- Image -->
				<img
					src={mendStore.image}
					alt="Scanning for damage"
					class="w-full h-full object-contain pointer-events-none select-none"
					draggable="false"
				/>

				<!-- Animated scanning bar -->
				<div class="scanning-bar"></div>
			</div>
		</div>

		<!-- Status text -->
		<div class="text-center p-4">
			<p class="text-gray-600">Scanning for damage...</p>
		</div>
	</main>
</div>

<style>
	.scanning-bar {
		position: absolute;
		left: 0;
		right: 0;
		height: 4px;
		background: var(--color-blue);
		box-shadow: 0 0 8px rgba(173, 215, 247, 0.6);
		animation: scan 2s ease-in-out infinite;
	}

	@keyframes scan {
		0%,
		100% {
			top: 0;
		}
		50% {
			top: calc(100% - 4px);
		}
	}
</style>
