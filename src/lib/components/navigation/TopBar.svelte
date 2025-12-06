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

<div class="relative flex items-center justify-center p-4 border-b border-border">
	{#if showBackButton}
		<div class="absolute left-4">
			<BackButton destination={backDestination} onclick={backHandler} />
		</div>
	{/if}
	<h1 class="text-center my-0">{title}</h1>
</div>
