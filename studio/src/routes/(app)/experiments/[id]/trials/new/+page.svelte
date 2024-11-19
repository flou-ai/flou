<script lang="ts">
	import type { PageData } from './$types';
	import { goto } from '$app/navigation';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';
	import Block from '$lib/UI/Block.svelte';
	import Select from '$lib/UI/Select.svelte';
	import { superForm, setMessage, setError } from 'sveltekit-superforms';
	import { _newTrialSchema } from './+page';
	import { zod } from 'sveltekit-superforms/adapters';

	export let data: PageData;

	$: ({experiment, params, registryOptions} = data)

	const { form, errors, message, constraints, enhance, isTainted } = superForm(data.form, {
		SPA: true,
		dataType: 'json',
		validators: zod(_newTrialSchema),
		onUpdate({ form }) {
			if (form.valid) {
			handleSubmit(form.data)
			}
		}
	});

	let handleSubmit = async (formData: any) => {
		let url = `${PUBLIC_API_BASE_URL}experiments/${experiment.id}/trials`;

		await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(formData)
		})
			.then((response) => response.json())
			.then((data) => {
				goto(`/playground/${data.id}`);
			})
			.catch((error) => {
				console.error('Error:', error);
			});
	};
</script>

<h2>New Trial</h2>
<Block>
	{#if $message}<div>{$message}</div>{/if}
	<form use:enhance>
		<div>

		Create a new Trial for experiment <b>#{experiment.index} {experiment.name}</b>.
		</div>

		<p>Choose from the following:</p>

		<label>
			Name
			<input
				aria-invalid={$errors.name ? 'true' : undefined}
				bind:value={$form.name}
				{...$constraints.name}
			/>
		</label>
		{#if $errors.name}<span class="invalid">{$errors.name}</span>{/if}
		<Select
			ariaInvalid={$errors.fqn ? 'true' : undefined}
			bind:value={$form.fqn}
			{...$constraints.fqn}
			options={data.registryOptions}
			label="LTM"
			emptyLabel="Select LTM"
		/>
		{#if $errors.fqn && isTainted('fqn')}<span class="invalid">{$errors.fqn}</span>{/if}
		<label>
			Inputs (JSON)
			<textarea
				aria-invalid={$errors.inputs ? 'true' : undefined}
				bind:value={$form.inputs}
				{...$constraints.inputs}
			/>
		</label>
		{#if $errors.inputs}<span class="invalid">{$errors.inputs}</span>{/if}

		<div class="buttons full-width">
			<a class="button secondary large" href="/experiments">Cancel</a>
			<button type="submit" class="primary large">Create Trial</button>
		</div>
	</form>
</Block>
