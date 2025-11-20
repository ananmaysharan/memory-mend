<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		children: Snippet;
		disabled?: boolean;
		onclick?: () => void;
		type?: 'button' | 'submit' | 'reset';
	}

	let { children, disabled = false, onclick, type = 'button' }: Props = $props();
</script>

<button {type} {disabled} {onclick}>
	{@render children()}
</button>
