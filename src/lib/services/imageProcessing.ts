/**
 * Image processing service
 * Currently basic preprocessing - will add YOLOv8 and ArUco detection later
 */

import type { Detection } from '$lib/types/mend';
import { resize43Image, compressImage } from '$lib/utils/imageUtils';

/**
 * Preprocess an image for analysis
 * Resizes to 3:4 aspect ratio (1200x1600) and compresses
 */
export async function preprocessImage(base64Image: string): Promise<string> {
	// Resize to 3:4 aspect ratio at 1200x1600
	const resized = await resize43Image(base64Image, 1200);

	// Compress to reduce file size
	const compressed = await compressImage(resized, 0.85);

	return compressed;
}

/**
 * YOLOv8 damage detection via FastAPI backend
 * Sends image to API and returns detection with highest confidence
 */
export async function detectDamage(base64Image: string, confidenceThreshold = 0.3): Promise<Detection | null> {
	// Get API URL from environment variable (defaults to localhost for dev)
	const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001';

	try {
		const response = await fetch(`${apiUrl}/detect`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				image: base64Image,
				confidence_threshold: confidenceThreshold
			})
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.detail || `API error: ${response.status}`);
		}

		const data = await response.json();

		// Return the first (highest confidence) detection if any found
		if (data.detections && data.detections.length > 0) {
			const firstDetection = data.detections[0];

			return {
				boundingBox: {
					x: firstDetection.bbox.x,
					y: firstDetection.bbox.y,
					width: firstDetection.bbox.width,
					height: firstDetection.bbox.height
				},
				confidence: firstDetection.confidence,
				className: firstDetection.class_name
			};
		}

		// No detections found
		return null;

	} catch (error) {
		console.error('Error calling detection API:', error);

		// Re-throw with more context
		if (error instanceof TypeError && error.message.includes('fetch')) {
			throw new Error('Could not connect to detection API.');
		}

		throw error;
	}
}

/**
 * Detect ArUco markers in an image
 * TODO: Implement ArUco detection
 */
export async function detectArucoMarkers(base64Image: string): Promise<any[]> {
	// Placeholder for future implementation
	console.log('ArUco detection not yet implemented');
	return [];
}

/**
 * Apply basic image enhancements
 */
export async function enhanceImage(base64Image: string): Promise<string> {
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

			// Draw original image
			ctx.drawImage(img, 0, 0);

			// Apply brightness/contrast adjustments
			const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
			const data = imageData.data;

			const brightness = 1.1;
			const contrast = 1.2;

			for (let i = 0; i < data.length; i += 4) {
				// Apply brightness
				data[i] *= brightness;
				data[i + 1] *= brightness;
				data[i + 2] *= brightness;

				// Apply contrast
				data[i] = ((data[i] - 128) * contrast + 128);
				data[i + 1] = ((data[i + 1] - 128) * contrast + 128);
				data[i + 2] = ((data[i + 2] - 128) * contrast + 128);

				// Clamp values
				data[i] = Math.min(255, Math.max(0, data[i]));
				data[i + 1] = Math.min(255, Math.max(0, data[i + 1]));
				data[i + 2] = Math.min(255, Math.max(0, data[i + 2]));
			}

			ctx.putImageData(imageData, 0, 0);
			resolve(canvas.toDataURL('image/jpeg', 0.9));
		};

		img.onerror = reject;
		img.src = base64Image;
	});
}
