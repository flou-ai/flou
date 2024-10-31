<script lang="ts">
	import { ClockCounterClockwise, Lifebuoy } from 'phosphor-svelte';
    import { createEventDispatcher } from 'svelte';

	import Paginator from '$lib/UI/Paginator.svelte';
    import { PUBLIC_API_BASE_URL } from '$env/static/public';

    let dispatch = createEventDispatcher();

	export let ltm: any;
    export let ltmId;
    let index = 0;

	const ltmUrl = `${PUBLIC_API_BASE_URL}ltm/${ltmId}`;

	let recoverRollback = async (snapshot_index: number) => {
		let postData = {
			index: snapshot_index,
		};
		await fetch(`${ltmUrl}/recover-rollback`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(postData)
		})
			.then((response) => {
                dispatch('reloadLtm');
				return response.json();
			})
			.then((data) => {})
			.catch((error) => {
				console.log(error);
			});
	};
</script>

<h3><ClockCounterClockwise size="1.25rem" />Rollbacks</h3>
	<table>
		<tr>
			<th>Reason</th>
			<th>#Snapshots</th>
			<th>Last Snapshot</th>
			<th>Time</th>
			<th></th>
		</tr>
		{#each ltm.rollbacks as rollback, i}
            {@const lastSnapshot = rollback.snapshots.at(-1)}
			<tr
				class:current={i === index}
				on:click={() => index = i}
				on:keydown={() => index = i}
				role="button"
			>
				<td title={rollback.reason}>{rollback.reason}</td>
				<td title={rollback.snapshots.length}>{JSON.stringify(rollback.snapshots.length)}</td>
				<td title={`${lastSnapshot.reason}: ${lastSnapshot.name}`}>{lastSnapshot.reason}: {lastSnapshot.name}</td>
				<td title={rollback.time}>{rollback.time}</td>
				<td>
					<div class="snapshot-controls">
						<button
							on:click={() => {
								recoverRollback(i);
							}}
							title="Recover rollback"
						>
							<Lifebuoy size="1.25rem" />
						</button>
                    </td>
			</tr>{/each}
	</table>
	<Paginator bind:index={index} collection={ltm.rollbacks} />