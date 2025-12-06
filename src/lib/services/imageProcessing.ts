/**
 * Image processing service
 * YOLOv8 damage detection via FastAPI backend
 */

import type { Detection } from '$lib/types/mend';

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
