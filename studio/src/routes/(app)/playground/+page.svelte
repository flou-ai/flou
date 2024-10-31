<script lang="ts">
	import WebSocket from '$lib/WebSocket.svelte';
	import { onMount } from 'svelte';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';

	import { ListMagnifyingGlass, Plus } from 'phosphor-svelte';

	const listUrl = `${PUBLIC_API_BASE_URL}ltm/?playground=true`;
	let ltms: any[] = [];

	onMount(async () => {
		await getLTMs();
	});

	// Get the snapshots from the API
	let getLTMs = async () => {
		await fetch(listUrl)
			.then((response) => response.json())
			.then((data) => {
				ltms = data;
			})
			.catch((error) => {
				console.log(error);
				return [];
			});
	};

	const formatDate = (dateString: string) => {
		const options: Intl.DateTimeFormatOptions = {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		};
		return new Date(dateString).toLocaleDateString(undefined, options);
	};
</script>

<h2>Playground</h2>

<div class="table-header">
	<h3>LTMs</h3>
	<div class="table-controls">
		<a href="/playground/new">
			<Plus size="1rem" /> New LTM
		</a>
	</div>
</div>

{#if ltms}
	<table>
		<tr>
			<th>ID</th>
			<th>Name</th>
			<th>FQN</th>
			<th># Snapshots</th>
			<th>Created At</th>
			<th>Updated At</th>
			<th></th>
		</tr>
		{#each ltms as ltm}
			<tr>
				<td>{ltm.id}</td>
				<td>{ltm.name}</td>
				<td>{ltm.fqn}</td>
				<td>{ltm.snapshots_count}</td>
				<td>{ltm.created_at}</td>
				<td>{ltm.updated_at}</td>
				<td>
					<a href="playground/{ltm.id}">
						<ListMagnifyingGlass size="1.25rem" />
					</a>
				</td>
				<!-- <td>Updated At: {formatDate(ltm.updated_at)}</td> -->
			</tr>
		{/each}
	</table>
{:else}
	<p>Loading...</p>
{/if}

<style lang="scss">
	.table-header {
		display: flex;
		justify-content: space-between;
	}

	.table-controls {
		display: flex;
		align-items: center;
		justify-content: end;
		padding: 0 1rem;

		a {
			display: flex;
			align-items: center;
			gap: 0.5rem;
			color: var(--black-40, rgba(28, 28, 28, 0.40));
			text-decoration: none;

			&:hover {
				color: var(--black-100, #1c1c1c);
			}
		}
	}
</style>

<WebSocket ltmID="56"/>