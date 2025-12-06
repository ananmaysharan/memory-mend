/**
 * Mend workflow state store using Svelte 5 runes
 * Manages the current mend being created
 */

import type { Mend, Memory, PatternData, Detection } from '$lib/types/mend';
import { saveCurrentMend, getCurrentMend, clearCurrentMend } from '$lib/utils/storage';
import { generatePatternFromMemory } from '$lib/services/patternGenerator';

class MendStore {
	// Current workflow step
	step = $state<'capture' | 'detection' | 'memory' | 'pattern' | 'preview'>('capture');

	// Garment details
	garmentType = $state<string | null>(null);
	material = $state<string | null>(null);
	fabricConstruction = $state<string | null>(null);

	// Captured image
	image = $state<string | null>(null);

	// YOLOv8 detection result (optional)
	detection = $state<Detection | null>(null);

	// Track if detection has been attempted (to avoid re-running)
	detectionAttempted = $state<boolean>(false);

	// Detection error message (if detection failed)
	detectionError = $state<string | null>(null);

	// Memory data
	memory = $state<Memory | null>(null);

	// Generated/edited pattern
	pattern = $state<PatternData | null>(null);

	// Track if pattern animation has been shown
	patternAnimationShown = $state<boolean>(false);

	// Mend ID (generated when saving)
	id = $state<string | null>(null);

	constructor() {
		// Load any saved workflow state
		if (typeof window !== 'undefined') {
			this.loadFromStorage();
		}
	}

	/**
	 * Load workflow state from storage
	 */
	loadFromStorage() {
		const saved = getCurrentMend();
		if (saved) {
			this.garmentType = saved.garmentType || null;
			this.material = saved.material || null;
			this.fabricConstruction = saved.fabricConstruction || null;
			this.image = saved.image || null;
			this.detection = saved.detection || null;
			this.memory = saved.memory || null;
			this.pattern = saved.pattern || null;
			this.id = saved.id || null;
		}
	}

	/**
	 * Save current state to storage
	 */
	saveToStorage() {
		saveCurrentMend({
			garmentType: this.garmentType || undefined,
			material: this.material || undefined,
			fabricConstruction: this.fabricConstruction || undefined,
			image: this.image || undefined,
			detection: this.detection || undefined,
			memory: this.memory || undefined,
			pattern: this.pattern || undefined,
			id: this.id || undefined
		});
	}

	/**
	 * Set captured image with garment details
	 */
	setImage(imageData: string, garmentType: string, material: string, fabricConstruction: string) {
		this.image = imageData;
		this.garmentType = garmentType;
		this.material = material;
		this.fabricConstruction = fabricConstruction;
		this.detection = null;
		this.detectionAttempted = false;
		this.detectionError = null;
		this.step = 'detection';
		this.saveToStorage();
	}

	/**
	 * Set detection result (from YOLOv8 or manual)
	 */
	setDetection(detectionData: Detection | null, errorMessage: string | null = null) {
		this.detection = detectionData;
		this.detectionAttempted = true;
		this.detectionError = errorMessage;
		this.saveToStorage();
	}

	/**
	 * Set memory and generate pattern
	 */
	async setMemory(memoryData: Memory) {
		this.memory = memoryData;

		// Generate pattern from memory
		const pattern = await generatePatternFromMemory(memoryData);
		this.pattern = pattern;
		this.patternAnimationShown = false; // Reset animation flag for new pattern

		this.step = 'pattern';
		this.saveToStorage();
	}

	/**
	 * Update pattern (when user edits)
	 */
	setPattern(patternData: PatternData) {
		this.pattern = patternData;
		this.saveToStorage();
	}

	/**
	 * Go to preview step
	 */
	goToPreview() {
		if (!this.pattern) {
			throw new Error('No pattern available');
		}
		this.step = 'preview';
		this.saveToStorage();
	}

	/**
	 * Go to a specific step
	 */
	goToStep(newStep: 'capture' | 'detection' | 'memory' | 'pattern' | 'preview') {
		this.step = newStep;
	}

	/**
	 * Reset the entire workflow
	 */
	reset() {
		this.step = 'capture';
		this.garmentType = null;
		this.material = null;
		this.fabricConstruction = null;
		this.image = null;
		this.detection = null;
		this.detectionAttempted = false;
		this.detectionError = null;
		this.memory = null;
		this.pattern = null;
		this.patternAnimationShown = false;
		this.id = null;
		clearCurrentMend();
	}

	/**
	 * Get the current mend as a complete object
	 */
	getMend(): Partial<Mend> {
		return {
			id: this.id || undefined,
			garmentType: this.garmentType || undefined,
			material: this.material || undefined,
			fabricConstruction: this.fabricConstruction || undefined,
			image: this.image || undefined,
			detection: this.detection || undefined,
			memory: this.memory || undefined,
			pattern: this.pattern || undefined
		};
	}

	/**
	 * Check if we can proceed to the next step
	 */
	canProceed(fromStep: 'capture' | 'detection' | 'memory' | 'pattern'): boolean {
		switch (fromStep) {
			case 'capture':
				return this.image !== null;
			case 'detection':
				// Detection is optional - can proceed even without detection
				return this.image !== null;
			case 'memory':
				return this.memory !== null && this.pattern !== null;
			case 'pattern':
				return this.pattern !== null;
			default:
				return false;
		}
	}
}

// Export singleton instance
export const mendStore = new MendStore();
