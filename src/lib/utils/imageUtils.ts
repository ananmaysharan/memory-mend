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
 * Resize and crop image to 3:4 aspect ratio (vertical)
 * This ensures consistent aspect ratio across the app
 */
export async function resize43Image(
	base64: string,
	targetWidth: number = 1200
): Promise<string> {
	return new Promise((resolve, reject) => {
		const img = new Image();

		img.onload = () => {
			const targetHeight = Math.round(targetWidth / (3 / 4));
			const sourceRatio = img.width / img.height;
			const targetRatio = 3 / 4;

			let sourceWidth = img.width;
			let sourceHeight = img.height;
			let offsetX = 0;
			let offsetY = 0;

			if (sourceRatio > targetRatio) {
				// Source is wider - crop width (center crop)
				sourceWidth = sourceHeight * targetRatio;
				offsetX = (img.width - sourceWidth) / 2;
			} else if (sourceRatio < targetRatio) {
				// Source is taller - crop height (center crop)
				sourceHeight = sourceWidth / targetRatio;
				offsetY = (img.height - sourceHeight) / 2;
			}

			const canvas = document.createElement('canvas');
			canvas.width = targetWidth;
			canvas.height = targetHeight;

			const ctx = canvas.getContext('2d');
			if (!ctx) {
				reject(new Error('Failed to get canvas context'));
				return;
			}

			// Draw the cropped and resized image
			ctx.drawImage(
				img,
				offsetX,
				offsetY,
				sourceWidth,
				sourceHeight,
				0,
				0,
				targetWidth,
				targetHeight
			);

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
