<script lang="ts">
	import type { PageData } from './$types';
	import { goto } from '$app/navigation';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';
	import Block from '$lib/UI/Block.svelte';
	import Select from '$lib/UI/Select.svelte';
	import { superForm, setMessage, setError } from 'sveltekit-superforms';
	import { _newExperimentSchema } from './+page';
	import { zod } from 'sveltekit-superforms/adapters';

	export let data: PageData;

	const { form, errors, message, constraints, enhance } = superForm(data.form, {
		SPA: true,
		dataType: 'json',
		validators: zod(_newExperimentSchema),
		onUpdate({ form }) {
			if (form.valid) {
			handleSubmit(form.data)
			}
		}
	});

	let handleSubmit = async (data: any) => {
		let url = `${PUBLIC_API_BASE_URL}experiments`;

		await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(data)
		})
			.then((response) => response.json())
			.then((data) => {
				// goto(`/experiments/${data.id}`);
			})
			.catch((error) => {
				console.error('Error:', error);
			});
	};
</script>

<h2>New Experiment</h2>
<Block>
	{#if $message}<div>{$message}</div>{/if}
	<form use:enhance>
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
		<label>
			Description
			<textarea
				aria-invalid={$errors.description ? 'true' : undefined}
				bind:value={$form.description}
				{...$constraints.description}
			/>
		</label>
		<label>
			First Trial Name
			<input
				aria-invalid={$errors.trial?.name ? 'true' : undefined}
				bind:value={$form.trial.name}
				{...$constraints.trial?.name}
			/>
		</label>
		<Select
			ariaInvalid={$errors.trial?.fqn ? 'true' : undefined}
			bind:value={$form.trial.fqn}
			{...$constraints.trial?.fqn}
			options={data.registryOptions}
			label="LTM"
			emptyLabel="Select LTM"
		/>
		<div class="buttons full-width">
			<a class="button secondary large" href="/experiments">Cancel</a>
			<button type="submit" class="primary large">Create Experiment</button>
		</div>
	</form>
</Block>
