<script lang="ts">
	import { Combobox } from 'bits-ui';

	interface Option {
		value: string;
		label: string;
	}

	interface Props {
		options: Option[];
		label: string;
		placeholder?: string;
		value: string;
	}

	let { options, label, placeholder = 'Select an option', value = $bindable() }: Props = $props();

	let searchValue = $state('');
	let open = $state(false);

	const filteredOptions = $derived(
		searchValue === ''
			? options
			: options.filter((option) =>
					option.label.toLowerCase().includes(searchValue.toLowerCase())
				)
	);

	function handleOpenChange(newOpen: boolean) {
		open = newOpen;
		if (!newOpen) searchValue = '';
	}

	function handleInputClick() {
		open = true;
	}
</script>

<div class="w-full">
	<label class="block mb-2 textmd">{label}</label>
	<Combobox.Root
		type="single"
		bind:value
		bind:open
		onOpenChange={handleOpenChange}
	>
		<div class="relative">
			<Combobox.Input
				oninput={(e) => (searchValue = e.currentTarget.value)}
				onclick={handleInputClick}
				class="w-full h-11 px-4 pr-12 border border-gray-300 rounded focus:outline-none focus:border-gray-500"
				{placeholder}
				aria-label={label}
			/>
			<Combobox.Trigger
				class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 pointer-events-auto w-auto! p-0! m-0! bg-transparent! border-0! shadow-none! rounded-none! hover:bg-transparent! active:bg-transparent! normal-case"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
				</svg>
			</Combobox.Trigger>
		</div>
		<Combobox.Portal>
			<Combobox.Content
				class="z-50 max-h-96 w-[var(--bits-combobox-anchor-width)] border border-gray-300 bg-white rounded overflow-hidden"
				sideOffset={4}
			>
				<Combobox.Viewport class="p-1">
					{#each filteredOptions as option (option.value)}
						<Combobox.Item
							class="px-4 py-2.5 text-sm cursor-pointer hover:bg-gray-100 outline-none font-mono data-[highlighted]:bg-gray-100"
							value={option.value}
							label={option.label}
						>
							{#snippet children({ selected })}
								<div class="flex items-center justify-between">
									<span>{option.label}</span>
									{#if selected}
										<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
										</svg>
									{/if}
								</div>
							{/snippet}
						</Combobox.Item>
					{:else}
						<div class="px-4 py-2.5 text-sm text-gray-500 font-mono">
							No results found
						</div>
					{/each}
				</Combobox.Viewport>
			</Combobox.Content>
		</Combobox.Portal>
	</Combobox.Root>
</div>
