/**
 * Storage abstraction layer - currently uses localStorage,
 * can be easily swapped to API calls later
 */

import type { Mend } from '$lib/types/mend';

const STORAGE_KEYS = {
	MENDS: 'memory-mend:mends',
	CURRENT_MEND: 'memory-mend:current-mend'
};

/**
 * Check if localStorage is available
 */
function isLocalStorageAvailable(): boolean {
	try {
		const test = '__storage_test__';
		localStorage.setItem(test, test);
		localStorage.removeItem(test);
		return true;
	} catch {
		return false;
	}
}

/**
 * Get all saved mends from storage
 */
export function getAllMends(): Mend[] {
	if (!isLocalStorageAvailable()) return [];

	try {
		const data = localStorage.getItem(STORAGE_KEYS.MENDS);
		return data ? JSON.parse(data) : [];
	} catch (error) {
		console.error('Error reading mends from storage:', error);
		return [];
	}
}

/**
 * Save a mend to storage
 */
export function saveMend(mend: Mend): void {
	if (!isLocalStorageAvailable()) {
		console.warn('localStorage not available');
		return;
	}

	try {
		const mends = getAllMends();
		const existingIndex = mends.findIndex((m) => m.id === mend.id);

		if (existingIndex >= 0) {
			// Update existing mend
			mends[existingIndex] = { ...mend, updatedAt: Date.now() };
		} else {
			// Add new mend
			mends.push(mend);
		}

		localStorage.setItem(STORAGE_KEYS.MENDS, JSON.stringify(mends));
	} catch (error) {
		console.error('Error saving mend to storage:', error);
	}
}

/**
 * Get a specific mend by ID
 */
export function getMendById(id: string): Mend | null {
	const mends = getAllMends();
	return mends.find((m) => m.id === id) || null;
}

/**
 * Delete a mend from storage
 */
export function deleteMend(id: string): void {
	if (!isLocalStorageAvailable()) return;

	try {
		const mends = getAllMends();
		const filtered = mends.filter((m) => m.id !== id);
		localStorage.setItem(STORAGE_KEYS.MENDS, JSON.stringify(filtered));
	} catch (error) {
		console.error('Error deleting mend from storage:', error);
	}
}

/**
 * Save current workflow state (draft mend)
 */
export function saveCurrentMend(data: Partial<Mend>): void {
	if (!isLocalStorageAvailable()) return;

	try {
		localStorage.setItem(STORAGE_KEYS.CURRENT_MEND, JSON.stringify(data));
	} catch (error) {
		console.error('Error saving current mend:', error);
	}
}

/**
 * Get current workflow state
 */
export function getCurrentMend(): Partial<Mend> | null {
	if (!isLocalStorageAvailable()) return null;

	try {
		const data = localStorage.getItem(STORAGE_KEYS.CURRENT_MEND);
		return data ? JSON.parse(data) : null;
	} catch (error) {
		console.error('Error reading current mend:', error);
		return null;
	}
}

/**
 * Clear current workflow state
 */
export function clearCurrentMend(): void {
	if (!isLocalStorageAvailable()) return;
	localStorage.removeItem(STORAGE_KEYS.CURRENT_MEND);
}

/**
 * Clear all storage (useful for testing/reset)
 */
export function clearAllStorage(): void {
	if (!isLocalStorageAvailable()) return;
	Object.values(STORAGE_KEYS).forEach((key) => localStorage.removeItem(key));
}
