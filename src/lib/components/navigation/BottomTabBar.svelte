<script lang="ts">
	import { page } from '$app/stores';
	import House from 'phosphor-svelte/lib/House';
	import Users from 'phosphor-svelte/lib/Users';
	import Rows from 'phosphor-svelte/lib/Rows';
	import User from 'phosphor-svelte/lib/User';

	interface Tab {
		path: string;
		label: string;
		icon: typeof House;
	}

	const tabs: Tab[] = [
		{ path: '/', label: 'Home', icon: House },
		{ path: '/friends', label: 'Friends', icon: Users },
		{ path: '/mends', label: 'Mends', icon: Rows },
		{ path: '/profile', label: 'Profile', icon: User }
	];

	const isActive = (path: string) => $page.url.pathname === path;
</script>

<nav
	class="fixed bottom-0 left-0 right-0 bg-surface border-t border-border z-50"
	style="padding-bottom: env(safe-area-inset-bottom);"
>
	<div class="flex justify-around items-center h-16 max-w-3xl mx-auto">
		{#each tabs as tab}
			<a
				href={tab.path}
				class="flex flex-col items-center justify-center flex-1 py-2 font-mono uppercase text-xs transition-colors no-underline hover:no-underline hover:bg-off-white"
				class:text-orange-600={isActive(tab.path)}
				class:text-gray-600={!isActive(tab.path)}
			>
				<svelte:component
					this={tab.icon}
					size={24}
					weight={isActive(tab.path) ? 'fill' : 'regular'}
				/>
				<span class="mt-1">{tab.label}</span>
			</a>
		{/each}
	</div>
</nav>
