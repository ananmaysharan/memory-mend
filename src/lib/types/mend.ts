/**
 * Core type definitions for Memory Mend application
 */

/**
 * Represents a memory input by the user
 */
export interface Memory {
	id: string; // Hash of the memory content
	title?: string; // Memory title
	text?: string; // Text memory
	images?: string[]; // Array of base64 encoded images (max 6)
	timestamp: number;
}

/**
 * Damage detection result from YOLOv8 (future feature)
 */
export interface Detection {
	boundingBox: {
		x: number;
		y: number;
		width: number;
		height: number;
	};
	confidence: number;
	className: string;
}

/**
 * Binary pattern grid configuration
 */
export interface PatternConfig {
	gridSize: number; // Grid dimensions (e.g., 16x16 = 16)
	cellSize: number; // Size of each cell in pixels for display
}

/**
 * Stitch pattern data
 * NEW (2025-11-15): Patterns are now read-only representations of memory IDs
 */
export interface PatternData {
	grid: boolean[][]; // 2D array where true = stitch, false = no stitch
	id: string; // Short ID that was converted to this pattern (e.g., "A1B2C3")
	config: PatternConfig;
}

/**
 * Complete mend record
 */
export interface Mend {
	id: string; // Unique mend ID
	name?: string; // Optional user-given name
	garmentType?: string; // Type of clothing being mended
	material?: string; // Fabric/material type
	fabricConstruction?: string; // Fabric construction type (knit, woven, etc.)
	image: string; // Base64 encoded repair image
	memory: Memory;
	pattern: PatternData;
	detection?: Detection; // Future: YOLOv8 detection results
	createdAt: number;
	updatedAt: number;
	status: 'draft' | 'ready' | 'sent' | 'completed';
	isPublic?: boolean; // Privacy flag for Supabase sharing (default: true)
}

/**
 * Current mend workflow state
 */
export interface MendWorkflowState {
	step: 'capture' | 'memory' | 'pattern' | 'preview';
	garmentType: string | null;
	material: string | null;
	fabricConstruction: string | null;
	image: string | null;
	memory: Memory | null;
	pattern: PatternData | null;
}
