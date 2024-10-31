<script lang="ts">
	import { Play, ClockClockwise, ArrowArcLeft, Plus, Minus, Queue } from 'phosphor-svelte';
	import * as jsonpatch from 'fast-json-patch';
	import { createEventDispatcher } from 'svelte';
	import { isEqual } from 'lodash';
	import Tabs from '../UI/Tabs.svelte';
	import Tab from '../UI/Tab.svelte';

	import { PUBLIC_API_BASE_URL } from '$env/static/public';
	import Paginator from '$lib/UI/Paginator.svelte';
	import SnapshotItem from './SnapshotItem.svelte';

	export let ltm: any = {};
	export let ltmId: string | null = null;
	export let snapshotIndex = 0;
	export let snapshot: any = {};
	export let controls = false;

	const ltmUrl = `${PUBLIC_API_BASE_URL}ltm/${ltmId}`;

	let dispatch = createEventDispatcher();

	let showErrorDetails: any = {};

	$: {
		if (ltm && ltm.snapshots.length > 0) snapshot = getSnapshotFromIndex(snapshotIndex);
	}

	let addItemsToQueue = (queue: any[], newItems: any[]) => {
		// Remove the isNew flag from the items
		queue = queue.map((item: any) => {
			delete item['isNew'];
			return item;
		});

		// add new items with the isNew flag
		if (newItems) {
			queue.push(...newItems.map((item) => ({ ...item, isNew: true })));
		}

		return queue;
	};
	let getSnapshotFromIndex: any = (index: number) => {
		let full_snapshot: any = {
			state: {},
			executeQueue: [],
			transitionsQueue: []
		};
		for (let i = 0; i <= index; i++) {
			jsonpatch.applyPatch(full_snapshot['state'], jsonpatch.deepClone(ltm.snapshots[i]['patch']));
			full_snapshot.executeQueue = addItemsToQueue(
				full_snapshot.executeQueue,
				ltm.snapshots[i]['execute_queue']
			);
			full_snapshot.transitionsQueue = addItemsToQueue(
				full_snapshot.transitionsQueue,
				ltm.snapshots[i]['transitions_queue']
			);

			// Remove the current snapshot item from the queues
			const currentItem = ltm.snapshots[i]['item'];
			if (ltm.snapshots[i]['reason'] === 'transition') {
				full_snapshot.transitionsQueue = full_snapshot.transitionsQueue.filter(
					(item: any) => !isEqual(item, currentItem)
				);
			} else if (ltm.snapshots[i]['reason'] === 'execute') {
				full_snapshot.executeQueue = full_snapshot.executeQueue.filter(
					(item: any) => !isEqual(item, currentItem)
				);
			}
		}
		if (ltm.snapshots.length > 0 && index >= 1) {
			full_snapshot['time'] = ltm.snapshots[index]['time'];
			full_snapshot['reason'] = ltm.snapshots[index]['reason'];
			full_snapshot['item'] = ltm.snapshots[index]['item'];
		}
		return full_snapshot;
	};

	let rollback = async (snapshot_index: number) => {
		let postData = {
			index: snapshot_index
		};
		await fetch(`${ltmUrl}/rollback`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(postData)
		})
			.then((response) => {
				ltm = { ...ltm, snapshots: ltm.snapshots.slice(0, snapshot_index + 1) };
				dispatch('reloadLtm');
				return response.json();
			})
			.then((data) => {})
			.catch((error) => {
				console.log(error);
			});
	};

	let replay = async (snapshot_index: number) => {
		let postData = {
			index: snapshot_index
		};
		await fetch(`${ltmUrl}/replay`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(postData)
		})
			.then((response) => {
				snapshotIndex--;
				ltm = { ...ltm, snapshots: ltm.snapshots.slice(0, snapshot_index) };
				return response.json();
			})
			.then((data) => {
				dispatch('reloadLtm');
			})
			.catch((error) => {
				console.log(error);
			});
	};

	let retryAll = async () => {
		const ids = ltm.errors
			.filter((e: any) => e.success === false && e.retrying === false)
			.map((e: any) => e.id);
		retry(ids);
	};

	let retry = async (errorIds: string[]) => {
		let postData = { ids: errorIds };
		await fetch(`${ltmUrl}/retry`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(postData)
		})
			.then((response) => {
				return response.json();
			})
			.then((data) => {
				// dispatch('reloadLtm');
			})
			.catch((error) => {
				console.log(error);
			});
	};

	let errorsCount: number;
	$: {
		ltm;
		errorsCount = ltm.errors.filter((e: any) => e.retrying === false && e.success === false).length;
	}
</script>

<h3><ClockClockwise size="1.25rem" /> Execution History</h3>
<Tabs>
	<Tab title="Snapshots">
		<div class="controls">
			<table>
				<tr>
					<th>Reason</th>
					<th>Item</th>
					<th>Time</th>
					{#if controls}
						<th></th>
					{/if}
				</tr>
				{#each ltm.snapshots as snapshot, i}
					<tr
						class:current={i === snapshotIndex}
						on:click={() => (snapshotIndex = i)}
						on:keydown={() => (snapshotIndex = i)}
						role="button"
					>
						<td title={snapshot.reason}>{snapshot.reason}</td>
						<td title={JSON.stringify(snapshot.item)}>
							<SnapshotItem item={snapshot.item}></SnapshotItem>
						</td>
						<td title={snapshot.time}>{snapshot.time}</td>
						{#if controls}
							<td>
								<div class="snapshot-controls">
									<button
										on:click={() => {
											rollback(i);
										}}
										title="Rollback"
									>
										<ArrowArcLeft size="1.25rem" />
									</button>
									{#if snapshot.reason === 'transition' || snapshot.reason === 'start'}
										<button
											on:click={() => {
												replay(i);
											}}
											title="Replay"
										>
											<Play size="1.25rem" />
										</button>
									{/if}
								</div>
							</td>
						{/if}
					</tr>{/each}
			</table>
			<Paginator bind:index={snapshotIndex} collection={ltm.snapshots} />
		</div>
	</Tab>
	<Tab title={'Errors (' + errorsCount + ')'}>
		<div class="controls">
			<button on:click={retryAll} title="Retry All">
				<Queue size="1.25rem" /> Retry All
			</button>
			<table>
				<tr>
					<th>Reason</th>
					<th>Item</th>
					<th>Time</th>
					<th>Status</th>
					<th>Retries</th>
					{#if controls}
						<th></th>
					{/if}
				</tr>
				{#each ltm.errors as error, i}
					{@const lastRetry = error.retries.at(-1)}
					{@const status = error.success ? 'success' : error.retrying ? 'retrying' : 'error'}
					<tr>
						<td title={error.reason}>{error.reason}</td>
						<td title={JSON.stringify(error.item)}>
							<SnapshotItem item={error.item}></SnapshotItem>
						</td>
						<td title={lastRetry.time}>{lastRetry.time}</td>
						<td title={status}>{status}</td>
						<td title={error.retries.length}>{error.retries.length}</td>
						{#if controls}
							<td>
								<div class="snapshot-controls">
									{#if !showErrorDetails[error.id]}
										<button
											on:click={() => {
												showErrorDetails[error.id] = true;
											}}
											title="Show details"
										>
											<Plus size="1.25rem" />
										</button>
									{:else}
										<button
											on:click={() => {
												showErrorDetails[error.id] = false;
											}}
											title="Hide details"
										>
											<Minus size="1.25rem" />
										</button>
									{/if}
									{#if status === 'error'}
										<button
											on:click={() => {
												retry([error.id]);
											}}
											title="Retry"
										>
											<Play size="1.25rem" />
										</button>
									{/if}
								</div>
							</td>
						{/if}
					</tr>
					{#if showErrorDetails[error.id] === true}
						<tr>
							<td colspan="5" class="error-detail">
								{lastRetry.type}:
								{lastRetry.description}
								<pre>
									{lastRetry.details}
								</pre>
							</td>
						</tr>
					{/if}
				{/each}
			</table>
		</div>
	</Tab>
</Tabs>

<style lang="scss">
	.controls {
		display: flex;
		flex-direction: column;
		align-self: stretch;
		align-items: flex-end;
	}

	.snapshot-controls {
		display: flex;
	}

	.current td {
		background-color: var(--black-20);
	}
	.error-detail {
		text-align: left;
		padding: 0rem 1rem 1rem 1rem;
	}
	pre {
		font-size: 0.75rem;
		font-weight: 400;
		line-height: 1.125rem;
		font-family: monospace;
	}
</style>
