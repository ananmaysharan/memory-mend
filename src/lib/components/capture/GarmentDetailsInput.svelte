<script lang="ts">
	import Combobox from '$lib/components/ui/Combobox.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		garmentType: string;
		material: string;
		onCaptureImage: () => void;
		onUploadImage: () => void;
	}

	let { garmentType = $bindable(), material = $bindable(), onCaptureImage, onUploadImage }: Props = $props();

	const garmentOptions = [
		{ value: 'shirt', label: 'Shirt' },
		{ value: 'pants', label: 'Pants' },
		{ value: 'jacket', label: 'Jacket' },
		{ value: 'dress', label: 'Dress' },
		{ value: 'sweater', label: 'Sweater' },
		{ value: 'jeans', label: 'Jeans' },
		{ value: 'socks', label: 'Socks' },
		{ value: 'hat', label: 'Hat' },
		{ value: 'scarf', label: 'Scarf' },
		{ value: 'gloves', label: 'Gloves' },
		{ value: 'other', label: 'Other' }
	];

	const materialOptions = [
		{ value: 'cotton', label: 'Cotton' },
		{ value: 'denim', label: 'Denim' },
		{ value: 'wool', label: 'Wool' },
		{ value: 'polyester', label: 'Polyester' },
		{ value: 'silk', label: 'Silk' },
		{ value: 'linen', label: 'Linen' },
		{ value: 'fleece', label: 'Fleece' },
		{ value: 'leather', label: 'Leather' },
		{ value: 'other', label: 'Other' }
	];

	const isValid = $derived(garmentType !== '' && material !== '');

	function handleCaptureImage() {
		if (isValid) {
			onCaptureImage();
		}
	}

	function handleUploadImage() {
		if (isValid) {
			onUploadImage();
		}
	}
</script>

<div class="w-full h-full flex flex-col p-4">
	<div class="flex-1 flex flex-col justify-center max-w-md mx-auto w-full gap-6">
		<h2 class="text-2xl mb-4">Garment Details</h2>

		<Combobox
			bind:value={garmentType}
			options={garmentOptions}
			label="Type of Clothing"
			placeholder="Select garment type"
		/>

		<Combobox
			bind:value={material}
			options={materialOptions}
			label="Material"
			placeholder="Select material"
		/>

		<div class="flex flex-col gap-2.5 mt-6">
			<Button onclick={handleCaptureImage} disabled={!isValid}>
				Capture Image
			</Button>

			<p class="mx-auto italic text-center text-sm">or...</p>

			<Button onclick={handleUploadImage} disabled={!isValid}>
				Upload Image
			</Button>
		</div>
	</div>
</div>
