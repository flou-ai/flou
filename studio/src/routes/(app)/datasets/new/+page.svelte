<script lang="ts">
	import type { PageData } from './$types';
	import { goto } from '$app/navigation';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';
	import Block from '$lib/UI/Block.svelte';
	import Select from '$lib/UI/Select.svelte';
	import { superForm } from 'sveltekit-superforms';
	import { _newDatasetSchema } from './+page';
	import { zod } from 'sveltekit-superforms/adapters';

	export let data: PageData;

	const { form, errors, message, constraints, enhance } = superForm(data.form, {
		SPA: true,
		dataType: 'json',
		validators: zod(_newDatasetSchema),
		onUpdate({ form }) {
			if (form.valid) {
				handleSubmit(form.data);
			}
		}
	});

	let handleSubmit = async (data: any) => {
		let url = `${PUBLIC_API_BASE_URL}datasets/`;

		await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(data)
		})
			.then((response) => response.json())
			.then((data) => {
				goto(`/datasets/${data.id}`);
			})
			.catch((error) => {
				console.error('Error:', error);
			});
	};
</script>

<h2>New Dataset</h2>
<Block>
	{#if $message}<div class="error">{$message}</div>{/if}
	<form use:enhance>
		Create a dataset to store and manage your data.
		<p>Fill in the following details:</p>

		<label>
			Name
			<input
				aria-invalid={$errors.name ? 'true' : undefined}
				bind:value={$form.name}
				{...$constraints.name}
			/>
		</label>
		{#if $errors.name}<span class="invalid">{$errors.name}</span>{/if}

		<label>
			Description
			<br />
			Describe what kind of data this dataset will contain.
			<br />
			What's the purpose of this dataset? How will it be used?
			<textarea
				aria-invalid={$errors.description ? 'true' : undefined}
				bind:value={$form.description}
				{...$constraints.description}
			/>
		</label>
		{#if $errors.description}<span class="invalid">{$errors.description}</span>{/if}

		<Select
			ariaInvalid={$errors.schema_fqn ? 'true' : undefined}
			bind:value={$form.schema_fqn}
			{...$constraints.schema_fqn}
			options={data.schemaOptions}
			label="Schema"
			emptyLabel="Select Schema"
		/>
		{#if $errors.schema_fqn}<span class="invalid">{$errors.schema_fqn}</span>{/if}

		<div class="buttons full-width">
			<a class="button secondary large" href="/datasets">Cancel</a>
			<button type="submit" class="primary large">Create Dataset</button>
		</div>
	</form>
</Block>

<style lang="scss">
</style> 