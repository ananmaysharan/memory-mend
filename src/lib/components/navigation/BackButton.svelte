<script lang="ts">
	import { goto } from '$app/navigation';
	  import ArrowLeft from "phosphor-svelte/lib/ArrowLeft";


	interface Props {
		destination?: string;
		onclick?: () => void;
		label?: string;
	}

	let { destination, onclick, label = 'Back' }: Props = $props();

	function handleClick() {
		if (onclick) {
			onclick();
		} else if (destination) {
			goto(destination);
		}
	}
</script>

<button
	class="py-2 px-4 bg-transparent border border-border text-[#333] cursor-pointer text-sm w-auto normal-case shadow-none font-cooper hover:bg-off-white"
	onclick={handleClick}
>
	<ArrowLeft size={18} weight="bold" />
</button>
