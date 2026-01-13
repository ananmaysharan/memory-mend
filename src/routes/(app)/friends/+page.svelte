<script lang="ts">
	import TopBar from '$lib/components/navigation/TopBar.svelte';
	import pants from '$lib/assets/pants.png';
	import thrifted from '$lib/assets/thrifted.png';
	import sweater from '$lib/assets/sweater.png';
	import flannel from '$lib/assets/flannel.png';
	import cdgskirt from '$lib/assets/cdgskirt.png';

	// Mock data for the social feed
	const mockPosts = [
		{
			username: 'Jane',
			memoryTitle: "Mom's Pants from College",
			date: 'Dec 12',
			image: pants
		},
		{
			username: 'Ananmay',
			memoryTitle: "Thrifted Sweater",
			date: 'Dec 10',
			image: thrifted
		},
		{
			username: 'Jay',
			memoryTitle: 'High Fashion Sweater',
			date: 'Dec 8',
			image: sweater
		},
		{
			username: 'Lisa',
			memoryTitle: 'Flannel Shirt',
			date: 'Dec 5',
			image: flannel
		},
		{
			username: 'Emily',
			memoryTitle: "CDG Skirt",
			date: 'Dec 3',
			image: cdgskirt
		}
	];
</script>

<div class="page">
	<TopBar title="Feed" />
	<div class="page-content">
		<div class="max-w-md mx-auto flex flex-col">
			{#each mockPosts as post, index}
				<article class="flex flex-col gap-3 py-5">
					<!-- Post header -->
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<div class="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center">
								<span class="font-mono text-xs text-orange-600">{post.username[0]}</span>
							</div>
							<span class="font-mono text-sm text-gray-700">{post.username}'s Memory Mend</span>
						</div>
						<span class="text-sm text-gray-400 font-mono">{post.date}</span>
					</div>

					<!-- Memory title -->
					<h3 class="font-cooper text-lg font-semibold mb-0 capitalize">{post.memoryTitle}</h3>

					<!-- Polaroid image -->
					<div class="bg-white p-3 shadow-md w-full">
						<img
							src={post.image}
							alt={post.memoryTitle}
							class="w-full aspect-square object-cover"
						/>
					</div>
				</article>
			{/each}
		</div>
	</div>
</div>
