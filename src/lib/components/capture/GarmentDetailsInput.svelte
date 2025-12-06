<script lang="ts">
	import Select from '$lib/components/ui/Select.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Camera from "phosphor-svelte/lib/Camera";
	import UploadSimple from "phosphor-svelte/lib/UploadSimple";

	interface Props {
		garmentType: string;
		material: string;
		fabricConstruction: string;
		onCaptureImage: () => void;
		onUploadImage: () => void;
	}

	let { garmentType = $bindable(), material = $bindable(), fabricConstruction = $bindable(), onCaptureImage, onUploadImage }: Props = $props();

	const garmentOptions = [
		{ value: 'shirt', label: 'Shirt' },
		{ value: 'pants', label: 'Pants' },
		{ value: 'jacket', label: 'Jacket' },
		{ value: 'dress', label: 'Dress' },
		{ value: 'skirt', label: 'Skirt' },
		{ value: 'sweater', label: 'Sweater' },
		{ value: 'jeans', label: 'Jeans' },
		{ value: 'socks', label: 'Socks' },
		{ value: 'scarf', label: 'Scarf' },
		{ value: 'other', label: 'Other' }
	];

	const materialOptions = [
		{ value: 'cotton', label: 'Cotton' },
		{ value: 'denim', label: 'Denim' },
		{ value: 'wool', label: 'Wool' },
		{ value: 'jersey', label: 'Jersey' },
		{ value: 'polyester', label: 'Polyester' },
		{ value: 'silk', label: 'Silk' },
		{ value: 'linen', label: 'Linen' },
		{ value: 'fleece', label: 'Fleece' },
		{ value: 'other', label: 'Not Sure' }
	];

	const fabricConstructionOptions = [
		{ value: 'knit', label: 'Knit' },
		{ value: 'woven', label: 'Woven' },
		{ value: 'lace', label: 'Lace' },
		{ value: 'felt', label: 'Felt' },
		{ value: 'crochet', label: 'Crochet' },
		{ value: 'not-sure', label: 'Not Sure' }
	];

	const isValid = $derived(garmentType !== '' && material !== '' && fabricConstruction !== '');

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

		<Select
			bind:value={garmentType}
			options={garmentOptions}
			label="Garment Type"
			placeholder="Select garment type"
		/>

		<Select
			bind:value={material}
			options={materialOptions}
			label="Material"
			placeholder="Select material"
		/>

		<Select
			bind:value={fabricConstruction}
			options={fabricConstructionOptions}
			label="Fabric Construction"
			placeholder="Select fabric construction"
		/>

		<div class="flex flex-col gap-2.5 mt-6">
			<Button onclick={handleCaptureImage} disabled={!isValid}>
				<Camera size={18} weight="bold" /> Capture Image
			</Button>

			<p class="mx-auto italic text-center text-sm">or...</p>

			<Button onclick={handleUploadImage} disabled={!isValid}>
				<UploadSimple size={18} weight="bold" /> Upload Image
			</Button>
		</div>
	</div>
</div>
