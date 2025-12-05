/**
 * Scan Store - Temporary storage for scanned images during navigation
 *
 * This store holds the captured/uploaded image temporarily while navigating
 * from the scan page to the analyzing page. It does not persist to localStorage
 * as the data is only needed for a single navigation flow.
 */

class ScanStore {
	scannedImage = $state<string | null>(null);

	/**
	 * Set the scanned image to be analyzed
	 */
	setScannedImage(image: string) {
		this.scannedImage = image;
	}

	/**
	 * Clear the scanned image after it's been processed
	 */
	clearScannedImage() {
		this.scannedImage = null;
	}
}

export const scanStore = new ScanStore();
