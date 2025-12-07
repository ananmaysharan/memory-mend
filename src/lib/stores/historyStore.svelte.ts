/**
 * History store using Svelte 5 runes
 * Manages saved mends
 */

import type { Mend } from '$lib/types/mend';
import { getAllMends, saveMend, deleteMend as deleteFromStorage } from '$lib/utils/storage';
import { migrateAllMends } from '$lib/utils/patternMigration';

class HistoryStore {
	// List of all saved mends
	mends = $state<Mend[]>([]);
	// Track if migration is in progress
	migrating = $state(false);

	constructor() {
		// Load mends from storage on initialization
		if (typeof window !== 'undefined') {
			this.loadFromStorage();
		}
	}

	/**
	 * Load all mends from storage and migrate old patterns if needed
	 */
	async loadFromStorage() {
		const storedMends = getAllMends();

		// Migrate old patterns to new format
		this.migrating = true;
		const migratedMends = await migrateAllMends(storedMends);

		// Save migrated mends back to storage
		for (const mend of migratedMends) {
			try {
				saveMend(mend);
			} catch (error) {
				// Log but continue with other mends
				console.error('Failed to save migrated mend:', mend.id, error);
			}
		}

		this.mends = migratedMends;
		this.migrating = false;
	}

	/**
	 * Add a new mend to history
	 * @throws {Error} If save fails (e.g., quota exceeded)
	 */
	addMend(mend: Partial<Mend>): Mend {
		const now = Date.now();
		const completeMend: Mend = {
			id: mend.id || `mend-${now}`,
			name: mend.name,
			garmentType: mend.garmentType,
			material: mend.material,
			fabricConstruction: mend.fabricConstruction,
			image: mend.image || '',
			memory: mend.memory || { id: '', timestamp: now },
			pattern: mend.pattern || {
				grid: [],
				id: '',
				config: { gridSize: 8, cellSize: 20 }
			},
			detection: mend.detection,
			createdAt: mend.createdAt || now,
			updatedAt: now,
			status: mend.status || 'draft',
			isPublic: mend.isPublic,
			source: mend.source
		};

		try {
			saveMend(completeMend);
			this.loadFromStorage();
			return completeMend;
		} catch (error) {
			// Re-throw the error so the caller can handle it
			console.error('Failed to add mend to history:', error);
			throw error;
		}
	}

	/**
	 * Update an existing mend
	 */
	updateMend(id: string, updates: Partial<Mend>) {
		const existing = this.mends.find((m) => m.id === id);
		if (!existing) {
			throw new Error(`Mend with id ${id} not found`);
		}

		const updated: Mend = {
			...existing,
			...updates,
			id, // Ensure ID doesn't change
			updatedAt: Date.now()
		};

		saveMend(updated);
		this.loadFromStorage();
	}

	/**
	 * Delete a mend
	 */
	deleteMend(id: string) {
		deleteFromStorage(id);
		this.loadFromStorage();
	}

	/**
	 * Get a specific mend by ID
	 */
	getMendById(id: string): Mend | undefined {
		return this.mends.find((m) => m.id === id);
	}

	/**
	 * Get mends sorted by date (newest first)
	 */
	getSortedMends(): Mend[] {
		return [...this.mends].sort((a, b) => b.createdAt - a.createdAt);
	}

	/**
	 * Get mends by status
	 */
	getMendsByStatus(status: Mend['status']): Mend[] {
		return this.mends.filter((m) => m.status === status);
	}

	/**
	 * Search mends by name or memory text
	 */
	searchMends(query: string): Mend[] {
		const lowerQuery = query.toLowerCase();
		return this.mends.filter(
			(m) =>
				m.name?.toLowerCase().includes(lowerQuery) ||
				m.memory.text?.toLowerCase().includes(lowerQuery)
		);
	}

	/**
	 * Get total count of mends
	 */
	getCount(): number {
		return this.mends.length;
	}

	/**
	 * Get stats about mends
	 */
	getStats(): {
		total: number;
		draft: number;
		ready: number;
		sent: number;
		completed: number;
	} {
		return {
			total: this.mends.length,
			draft: this.getMendsByStatus('draft').length,
			ready: this.getMendsByStatus('ready').length,
			sent: this.getMendsByStatus('sent').length,
			completed: this.getMendsByStatus('completed').length
		};
	}

	/**
	 * Find a mend by its pattern ID
	 * @param patternId - The 6-character pattern ID (e.g., "A1B2C3")
	 * @returns The matching mend, or undefined if not found
	 */
	findMendByPatternId(patternId: string): Mend | undefined {
		return this.mends.find((m) => m.pattern.id === patternId);
	}
}

// Export singleton instance
export const historyStore = new HistoryStore();
