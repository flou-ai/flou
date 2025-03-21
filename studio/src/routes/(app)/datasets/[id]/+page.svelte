<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';
	import { ListMagnifyingGlass, Plus } from 'phosphor-svelte';
	import { formatDate } from '$lib/utils';
	import Block from '$lib/UI/Block.svelte';
	import InlineEditTextArea from '$lib/UI/InlineEditTextArea.svelte';

	const datasetId = $page.params.id;
	let dataset: any;
	let items: any[] = [];
	let error = '';

	onMount(async () => {
		await Promise.all([
			getDataset(),
			getItems()
		]);
	});

	const getDataset = async () => {
		try {
			const response = await fetch(`${PUBLIC_API_BASE_URL}datasets/${datasetId}`);
			if (!response.ok) {
				throw new Error('Dataset not found');
			}
			dataset = await response.json();
		} catch (err) {
			console.error('Error fetching dataset:', err);
			error = 'Failed to load dataset';
		}
	};

	const getItems = async () => {
		try {
			const response = await fetch(`${PUBLIC_API_BASE_URL}datasets/${datasetId}/items`);
			if (!response.ok) {
				throw new Error('Failed to load items');
			}
			items = await response.json();
		} catch (err) {
			console.error('Error fetching items:', err);
			error = 'Failed to load dataset items';
		}
	};

	function handleDescriptionSave(newDescription: string) {
		dataset.description = newDescription;
		// TODO: Add API call to update description
	}

	function handleNameSave(newName: string) {
		dataset.name = newName;
		// TODO: Add API call to update name
	}
</script>

{#if error}
	<div class="error">{error}</div>
{:else if !dataset}
	<p>Loading...</p>
{:else}
	<div class="container">
		<Block>
			<h2>
				#{dataset.index}
				<InlineEditTextArea
					value={dataset.name}
					on:save={(event) => handleNameSave(event.detail)}
				/>
			</h2>
			<dl class="details">
				<div>
					<dt># Items</dt>
					<dd>{items.length}</dd>
				</div>

				<div>
					<dt>Created At</dt>
					<dd>{formatDate(dataset.created_at)}</dd>
				</div>
				<div>
					<dt>Updated At</dt>
					<dd>{formatDate(dataset.updated_at)}</dd>
				</div>
				{#if dataset.schema_fqn}
					<div>
						<dt>Schema</dt>
						<dd>{dataset.schema_fqn}</dd>
					</div>
				{/if}
			</dl>
			<dl class="details">
				<div>
					<dt class="label">Description</dt>
					<dd>
						<InlineEditTextArea
							value={dataset.description}
							on:save={(event) => handleDescriptionSave(event.detail)}
						/>
					</dd>
				</div>
			</dl>
		</Block>

		<Block>
			<div class="table-header">
				<h3>Items</h3>
				<div class="table-controls">
					<a href="/datasets/{datasetId}/items/new">
						<Plus size="1rem" /> Add Item
					</a>
				</div>
			</div>
			{#if items.length === 0}
				<p>No items yet. Click "Add Item" to add your first item.</p>
			{:else}
				<table>
					<tr>
						<th>#</th>
						<th>Data</th>
						<th>Created At</th>
						<th>Updated At</th>
					</tr>
					{#each items as item}
						<tr>
							<td>{item.index}</td>
							<td>
								<pre>{JSON.stringify(item.data, null, 2)}</pre>
							</td>
							<td>{formatDate(item.created_at)}</td>
							<td>{formatDate(item.updated_at)}</td>
						</tr>
					{/each}
				</table>
			{/if}
		</Block>
	</div>
{/if}

<style lang="scss">
	:root {
		--horizontal-gap: 3rem;
	}

	.container {
		display: grid;
		gap: var(--20, 1.25rem);
	}

	.container > div {
		display: flex;
		flex-direction: column;
		position: relative;
	}

	.details {
		display: flex;
		gap: var(--horizontal-gap);
		flex-wrap: wrap;
	}

	.details > div {
		position: relative;
	}

	dt {
		font-size: 0.75rem;
		line-height: 1.25rem;
		margin-bottom: var(--4, 0.25rem);
		color: var(--black-40, rgba(28, 28, 28, 0.4));
	}

	dd {
		margin: 0;
		line-height: 1.5rem;
	}

	dl > div:not(:first-child) > dt::before {
		content: '';
		border-right: 1px solid var(--black-10, rgba(28, 28, 28, 0.1));
		position: absolute;
		height: 100%;
		transform: translatex(calc(-1 * var(--horizontal-gap) / 2));
	}

	.error {
		color: var(--secondary-red);
		margin-bottom: 1rem;
		padding: 0.5rem;
		border: 1px solid var(--secondary-red);
		border-radius: 0.25rem;
		background-color: var(--black-5);
	}

	pre {
		margin: 0;
		white-space: pre-wrap;
		word-break: break-all;
		font-size: 0.75rem;
		line-height: 1.25rem;
		color: var(--black-80);
	}

</style> 