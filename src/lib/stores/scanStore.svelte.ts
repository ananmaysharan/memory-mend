/**
 * Scan Store - Temporary storage for scanned images during navigation
 *
 * This store holds the captured/uploaded image temporarily while navigating
 * from the scan page to the analyzing page. It does not persist to localStorage
 * as the data is only needed for a single navigation flow.
 */

class ScanStore {
	scannedImage = $state<string | null>(null);
	detectionError = $state<string | null>(null);

	/**
	 * Set the scanned image to be analyzed
	 */
	setScannedImage(image: string) {
		this.scannedImage = image;
	}

	/**
	 * Set detection error message for display on manual decode page
	 */
	setDetectionError(error: string) {
		this.detectionError = error;
	}

	/**
	 * Clear detection error message
	 */
	clearDetectionError() {
		this.detectionError = null;
	}

	/**
	 * Clear the scanned image and error after they've been processed
	 */
	clearScannedImage() {
		this.scannedImage = null;
		this.detectionError = null;
	}
}

export const scanStore = new ScanStore();
