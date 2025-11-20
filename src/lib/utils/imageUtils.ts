/**
 * Image manipulation utilities
 */

/**
 * Convert a Blob to base64 string
 */
export async function blobToBase64(blob: Blob): Promise<string> {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.onloadend = () => {
			if (typeof reader.result === 'string') {
				resolve(reader.result);
			} else {
				reject(new Error('Failed to convert blob to base64'));
			}
		};
		reader.onerror = reject;
		reader.readAsDataURL(blob);
	});
}

/**
 * Convert base64 string to Blob
 */
export async function base64ToBlob(base64: string): Promise<Blob> {
	const response = await fetch(base64);
	return response.blob();
}

/**
 * Resize an image to maximum dimensions while maintaining aspect ratio
 */
export async function resizeImage(
	base64: string,
	maxWidth: number = 1920,
	maxHeight: number = 1080
): Promise<string> {
	return new Promise((resolve, reject) => {
		const img = new Image();

		img.onload = () => {
			let { width, height } = img;

			// Calculate new dimensions
			if (width > maxWidth || height > maxHeight) {
				const aspectRatio = width / height;

				if (width > height) {
					width = maxWidth;
					height = width / aspectRatio;
				} else {
					height = maxHeight;
					width = height * aspectRatio;
				}
			}

			// Create canvas and draw resized image
			const canvas = document.createElement('canvas');
			canvas.width = width;
			canvas.height = height;

			const ctx = canvas.getContext('2d');
			if (!ctx) {
				reject(new Error('Failed to get canvas context'));
				return;
			}

			ctx.drawImage(img, 0, 0, width, height);

			// Convert back to base64
			resolve(canvas.toDataURL('image/jpeg', 0.9));
		};

		img.onerror = reject;
		img.src = base64;
	});
}

/**
 * Compress an image to reduce file size
 */
export async function compressImage(base64: string, quality: number = 0.8): Promise<string> {
	return new Promise((resolve, reject) => {
		const img = new Image();

		img.onload = () => {
			const canvas = document.createElement('canvas');
			canvas.width = img.width;
			canvas.height = img.height;

			const ctx = canvas.getContext('2d');
			if (!ctx) {
				reject(new Error('Failed to get canvas context'));
				return;
			}

			ctx.drawImage(img, 0, 0);
			resolve(canvas.toDataURL('image/jpeg', quality));
		};

		img.onerror = reject;
		img.src = base64;
	});
}

/**
 * Get image dimensions from base64 string
 */
export async function getImageDimensions(
	base64: string
): Promise<{ width: number; height: number }> {
	return new Promise((resolve, reject) => {
		const img = new Image();

		img.onload = () => {
			resolve({ width: img.width, height: img.height });
		};

		img.onerror = reject;
		img.src = base64;
	});
}

/**
 * Crop image to a specific region
 */
export async function cropImage(
	base64: string,
	x: number,
	y: number,
	width: number,
	height: number
): Promise<string> {
	return new Promise((resolve, reject) => {
		const img = new Image();

		img.onload = () => {
			const canvas = document.createElement('canvas');
			canvas.width = width;
			canvas.height = height;

			const ctx = canvas.getContext('2d');
			if (!ctx) {
				reject(new Error('Failed to get canvas context'));
				return;
			}

			ctx.drawImage(img, x, y, width, height, 0, 0, width, height);
			resolve(canvas.toDataURL('image/jpeg', 0.9));
		};

		img.onerror = reject;
		img.src = base64;
	});
}
