<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';
	import Block from '$lib/UI/Block.svelte';
	import Select from '$lib/UI/Select.svelte';

	let registry: { name: string; fqn: string }[] | undefined;
	const registryUrl = `${PUBLIC_API_BASE_URL}ltm/registry`;

	let fqn: string;
	let payload: string;

	onMount(async () => {
		await getRegistry();
	});

	let getRegistry = async () => {
		await fetch(registryUrl)
			.then((response) => response.json())
			.then((data) => {
				registry = data;
			})
			.catch((error) => {
				console.log(error);
				return [];
			});
	};

	$: registryOptions = registry?.map((item) => {
		return [item.fqn, item.name];
	});

	let handleSubmit = async (event: SubmitEvent) => {
		let url = `${PUBLIC_API_BASE_URL}ltm`;
		let data: any = {
			fqn: fqn,
			playground: true
		};
		if (payload) {
			data['payload'] = JSON.parse(payload);
		}

		await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(data)
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

<Block>
	<h3>Create LTM</h3>

	{#if registry === undefined}
		Loading...
	{:else}
		<form on:submit|preventDefault={handleSubmit}>
			<p>Choose from the following:</p>
			<Select bind:value={fqn} options={registryOptions} label="LTM" emptyLabel="Select LTM" />
			<label>
				payload
				<textarea bind:value={payload} />
			</label>
			<div class="buttons full-width">
				<a class="button secondary large" href="/inspect">Cancel</a>
				<button type="submit" class="primary large" disabled={!fqn}>Create & Execute</button>
			</div>
		</form>
	{/if}
</Block>

<style lang="scss">
	h3 {
		margin: 0;
	}
</style>
