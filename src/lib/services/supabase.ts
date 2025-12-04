/**
 * Supabase Service
 * Handles global mend sharing via Supabase PostgreSQL database
 */

import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import type { Mend } from '$lib/types/mend';
import { idToBinary, binaryToGrid } from '$lib/utils/hashUtils';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';

// Supabase client instance
let supabase: SupabaseClient | null = null;

/**
 * Initialize and return Supabase client
 */
export function getSupabaseClient(): SupabaseClient | null {
	if (supabase) return supabase;

	const supabaseUrl = PUBLIC_SUPABASE_URL;
	const supabaseAnonKey = PUBLIC_SUPABASE_ANON_KEY;

	if (!supabaseUrl || !supabaseAnonKey) {
		console.warn('Supabase credentials not configured. Global sharing disabled.');
		return null;
	}

	supabase = createClient(supabaseUrl, supabaseAnonKey);
	return supabase;
}

/**
 * Check if Supabase is available and configured
 */
export function isSupabaseAvailable(): boolean {
	return getSupabaseClient() !== null;
}

/**
 * Upload a mend to Supabase (upsert on pattern_id)
 */
export async function uploadMendToSupabase(mend: Mend): Promise<{ success: boolean; error?: string }> {
	const client = getSupabaseClient();
	if (!client) {
		return { success: false, error: 'Supabase not configured' };
	}

	try {
		// Check if images are too large (>5MB total)
		let totalImageSize = 0;
		if (mend.memory.images) {
			for (const img of mend.memory.images) {
				// Rough estimate: base64 string length * 0.75 = bytes
				totalImageSize += img.length * 0.75;
			}
		}

		if (totalImageSize > 5 * 1024 * 1024) {
			console.warn('Images exceed 5MB, upload may be slow');
		}

		// Prepare data for upload
		const data = {
			pattern_id: mend.pattern.id,
			title: mend.memory.title || null,
			text: mend.memory.text || null,
			images: mend.memory.images || null,
			garment_type: mend.garmentType || null,
			material: mend.material || null,
			updated_at: new Date().toISOString()
		};

		// Upsert (insert or update if pattern_id exists)
		const { error } = await client
			.from('mends')
			.upsert(data, { onConflict: 'pattern_id' });

		if (error) {
			console.error('Supabase upload error:', error);
			return { success: false, error: error.message };
		}

		return { success: true };
	} catch (err) {
		console.error('Supabase upload exception:', err);
		return {
			success: false,
			error: err instanceof Error ? err.message : 'Unknown error'
		};
	}
}

/**
 * Find a mend by pattern ID in Supabase
 */
export async function findMendByPatternId(patternId: string): Promise<Mend | null> {
	const client = getSupabaseClient();
	if (!client) {
		return null;
	}

	try {
		const { data, error } = await client
			.from('mends')
			.select('*')
			.eq('pattern_id', patternId)
			.single();

		if (error) {
			if (error.code === 'PGRST116') {
				// Not found - not an error
				return null;
			}
			console.error('Supabase query error:', error);
			return null;
		}

		if (!data) {
			return null;
		}

		// Reconstruct full Mend from database row
		// Need to regenerate pattern grid from pattern ID
		const binary = idToBinary(data.pattern_id);
		const gridSize = 7; // Default grid size for 6-character IDs
		const grid = binaryToGrid(binary, gridSize);

		// Create memory ID from pattern ID (same as used during creation)
		const memoryId = data.pattern_id;

		const mend: Mend = {
			id: data.id,
			image: '', // Supabase doesn't store the garment image (too large)
			pattern: {
				id: data.pattern_id,
				grid: grid,
				config: {
					gridSize: gridSize,
					cellSize: 28
				}
			},
			memory: {
				id: memoryId,
				title: data.title || '',
				text: data.text || '',
				images: data.images || [],
				timestamp: data.created_at
			},
			garmentType: data.garment_type || undefined,
			material: data.material || undefined,
			status: 'ready',
			createdAt: data.created_at,
			updatedAt: data.updated_at,
			isPublic: true // If it's in Supabase, it's public
		};

		return mend;
	} catch (err) {
		console.error('Supabase query exception:', err);
		return null;
	}
}
