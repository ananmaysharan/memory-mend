<script lang="ts">
	import BackButton from './BackButton.svelte';

	interface Props {
		title: string;
		showBackButton?: boolean;
		backDestination?: string;
		backHandler?: () => void;
	}

	let { title, showBackButton = false, backDestination, backHandler }: Props = $props();
</script>

<div class="flex items-center gap-2 p-4 border-b border-border">
	{#if showBackButton}
		<BackButton destination={backDestination} onclick={backHandler} />
	{/if}
	<h1 class="my-0 font-medium leading-none flex items-center">{title}</h1>
</div>
