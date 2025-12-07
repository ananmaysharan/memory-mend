<script lang="ts">
	import BottomTabBar from '$lib/components/navigation/BottomTabBar.svelte';

	let { children } = $props();
</script>

<div class="min-h-screen pb-16">
	{@render children()}
</div>

<BottomTabBar />
