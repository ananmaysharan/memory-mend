<script lang="ts">
	/**
	 * Detection page - YOLOv8 damage detection and editing
	 * User can view, adjust, or manually add bounding box before proceeding to memory
	 */

	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { mendStore } from '$lib/stores/mendStore.svelte';
	import { detectDamage } from '$lib/services/imageProcessing';
	import type { Detection } from '$lib/types/mend';
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import BoundingBoxEditor from '$lib/components/detection/BoundingBoxEditor.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	// Component state
	let isScanning = $state(false);
	let error = $state<string | null>(null);
	let detection = $state<Detection | null>(null);

	// Check if we have a captured image
	onMount(async () => {
		if (!mendStore.image) {
			// No image captured, redirect to capture page
			await goto('/capture');
			return;
		}

		// Automatically run detection when page loads
		await runDetection();
	});

	// Run YOLOv8 detection
	async function runDetection() {
		if (!mendStore.image) return;

		isScanning = true;
		error = null;

		try {
			const result = await detectDamage(mendStore.image);
			detection = result;

			// Store detection in mend store
			mendStore.setDetection(result);

		} catch (err) {
			console.error('Detection error:', err);
			error = err instanceof Error ? err.message : 'Failed to detect damage';

			// User can still manually add a box even if detection fails
			detection = null;

		} finally {
			isScanning = false;
		}
	}

	// Handle bounding box changes from editor
	function handleDetectionChange(newDetection: Detection | null) {
		detection = newDetection;
		mendStore.setDetection(newDetection);
	}

	// Continue to memory step
	async function continueToMemory() {
		// Detection is optional - user can proceed even without a box
		await goto('/memory');
	}

	// Go back to capture page
	async function goBack() {
		await goto('/capture');
	}
</script>

<div class="page h-screen">
	<!-- Top bar with back button -->
	<TopBar title="Damage Detection" showBackButton={true} backDestination="/capture" />

	<!-- Main content -->
	<main class="page-content flex-1 overflow-hidden flex flex-col">
		<!-- Bounding box editor -->
		<BoundingBoxEditor
			image={mendStore.image || ''}
			{detection}
			onChange={handleDetectionChange}
		/>

		<!-- Error message -->
		{#if error}
			<div class="mt-4 rounded-lg border-2 border-yellow-500 bg-yellow-50 p-4">
				<p class="font-medium text-yellow-800">⚠️ Detection Issue</p>
				<p class="mt-1 text-sm text-yellow-700">{error}</p>
				<p class="mt-2 text-sm text-yellow-700">
					You can still add a detection box manually or proceed without one.
				</p>
			</div>
		{/if}

		<!-- Action buttons -->
		<div class="mt-6 flex gap-3">
			<!-- Continue button -->
			<Button
				onclick={continueToMemory}
				disabled={isScanning}
			>
				Continue
			</Button>
		</div>
	</main>
</div>
