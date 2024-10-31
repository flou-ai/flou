<script lang="ts">
	import { onMount } from 'svelte';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';

	import { ListMagnifyingGlass, Plus } from 'phosphor-svelte';

	const listUrl = `${PUBLIC_API_BASE_URL}ltm/`;
	let ltms: any[];

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
		const options = {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		};
		return new Date(dateString).toLocaleDateString(undefined, options);
	};
</script>

<div class="table-header">
	<h3>LTMs</h3>
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
					<a href="inspect/{ltm.id}">
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
</style>
