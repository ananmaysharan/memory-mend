<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		children: Snippet;
		title?: string;
	}

	let { children, title }: Props = $props();
</script>

<div>
	{#if title}
		<h2>{title}</h2>
	{/if}
	{@render children()}
</div>
