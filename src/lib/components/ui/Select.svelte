<script lang="ts">
	import { Select } from 'bits-ui';

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

	const selectedLabel = $derived(
		value ? options.find((option) => option.value === value)?.label : placeholder
	);
</script>

<div class="w-full">
	<label class="block mb-2 textmd">{label}</label>
	<Select.Root type="single" bind:value items={options}>
		<Select.Trigger
			class="h-12 border font-serif bg-white border-gray-300 rounded focus:outline-none focus:border-gray-500 inline-flex items-center justify-between"
			aria-label={label}
		>
			<span class="text-gray-600 font-mono">{selectedLabel}</span>
			<svg class="w-5 h-5 text-gray-600 ml-auto shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</Select.Trigger>
		<Select.Portal>
			<Select.Content
				class="z-50 max-h-96 w-(--bits-select-anchor-width) border border-gray-300 bg-white rounded overflow-hidden shadow-lg"
				sideOffset={4}
			>
				<Select.Viewport class="p-1">
					{#each options as option (option.value)}
						<Select.Item
							class="px-4 py-2.5 text-sm cursor-pointer hover:bg-gray-100 outline-none font-mono data-highlighted:bg-gray-100"
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
						</Select.Item>
					{/each}
				</Select.Viewport>
			</Select.Content>
		</Select.Portal>
	</Select.Root>
</div>
