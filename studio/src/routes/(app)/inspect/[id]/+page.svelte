<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Block from '$lib/UI/Block.svelte';
	import LTMGraph from '$lib/UI/Graph/LTMGraph.svelte';
	import SnapshotsTable from '$lib/Components/SnapshotsTable.svelte';
	import Alert from '$lib/UI/Alert.svelte';
	import State from '$lib/Components/State.svelte';
	import SnapshotNav from '$lib/Components/SnapshotNav.svelte';
	import WebSocket from '$lib/WebSocket.svelte';
	import { TreeStructure, Pinwheel, Flask } from 'phosphor-svelte';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';
	import { formatDate } from '$lib/utils';

	import type { PageData } from './$types';
	export let data: PageData;

	$: ({ ltm, rollback, experiment, params } = data);

	const ltmUrl = `${PUBLIC_API_BASE_URL}ltm/${data.params.id}?rollbacks=True`;

	onMount(async () => {
		snapshotIndex = ltm.snapshots.length - 1;
	});

	// Get the snapshots from the API
	let getLtm = async () => {};

	// Get the snapshots from the API
	let copyLtm = async () => {
		await fetch(`${ltmUrl}/copy`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		})
			.then((response) => response.json())
			.then((data) => {
				goto(`/playground/${data.copy_id}`);
			})
			.catch((error) => {
				console.log(error);
				return [];
			});
	};

	///// Snapshots management //////

	let snapshot: any = {};
	let snapshotIndex = 0;

	let updateLtm = (event: CustomEvent) => {
		const data: any = event.detail;
		if ('snapshot' in data) {
			const snapshot = data.snapshot;
			ltm = { ...ltm, snapshots: [...ltm.snapshots, snapshot] };
			if (snapshotIndex === ltm.snapshots.length - 2) {
				snapshotIndex = ltm.snapshots.length - 1;
			}
		}
		if ('error' in data) {
			const error = data.error;
			const i = ltm.errors.findIndex((e: any) => e.id === error.id);
			let errors;
			if (i > -1) {
				errors = ltm.errors.toSpliced(i, 1, error);
			} else {
				errors = [...ltm.errors, error];
			}
			ltm = { ...ltm, errors: errors };
		}
	};

	let currentSnapshot: any = {};
	$: {
		if (ltm?.snapshots) {
			currentSnapshot = ltm.snapshots[snapshotIndex];
		} else {
			currentSnapshot = {};
		}
	}
</script>

<WebSocket ltmID={params.id} on:update={updateLtm} />
{#if experiment}
	<Alert level="info" icon={Flask}>
		This LTM is part of the experiment <b>#{experiment.index} {experiment.name}</b>. To view the
		experiment, click <a href="/experiments/{ltm.experiment_id}">here</a>.

		<p>Trial <b>{ltm.current_trial.name} #{ltm.current_trial.index}</b></p>
	</Alert>
{:else if rollback}
	<Alert level="info">
		You are currently viewing a rollback of the LTM. To view the latest version, click <a
			href="/playground/{data.params.id}">here</a
		>.
	</Alert>
{/if}
<div class="container">
	{#if ltm}
		<div id="title">
			<div class="info">
				<Block>
					<h2 slot="title"><TreeStructure size="1.25rem" /> {ltm.name}</h2>
					<div slot="controls">
						<button class="primary" on:click={copyLtm}>
							<Pinwheel size="1rem" /> Copy & Open LTM in Playground
						</button>
					</div>
					<dl class="details">
						<dt>ID</dt>
						<dd>{params.id}</dd>
						<dt>Fqn</dt>
						<dd>{ltm.fqn}</dd>
						<dt>Kwargs</dt>
						<dd>{JSON.stringify(ltm.kwargs)}</dd>
					</dl>
					<hr />
					<dl class="details">
						<dt>Created At</dt>
						<dd>{formatDate(ltm.created_at)}</dd>
						<dt>Updated At</dt>
						<dd>{formatDate(ltm.updated_at)}</dd>
					</dl>
				</Block>
			</div>
		</div>
		<div id="snapshots">
			<Block>
				<SnapshotsTable {ltm} bind:snapshot bind:snapshotIndex />
			</Block>
		</div>
		<div id="snapshot">
			<Block>
				<State fullSnapshot={snapshot} {currentSnapshot} />
			</Block>
		</div>
		<div id="graph">
			<Block>
				<div class="flex-column">
					<h3><TreeStructure size="1.25rem" />Visual representation</h3>
					<SnapshotNav {ltm} bind:snapshotIndex />
					<LTMGraph
						ltm={ltm.structure}
						state={snapshot}
						{currentSnapshot}
						concurrent={ltm.concurrent_instances}
					/>
				</div>
			</Block>
		</div>
	{:else}
		<p>Loading...</p>
	{/if}
</div>

<style lang="scss">
	.container {
		display: grid;
		gap: var(--20, 1.25rem);
		// grid-template-areas: 'graph graph' 'snapshot title';
		grid-template-areas: 'title title' 'graph graph' 'snapshots snapshot';
		grid-template-columns: auto auto;
	}
	.container > div {
		display: flex;
		flex-direction: column;
	}
	#title {
		grid-area: title;
	}
	#snapshots {
		grid-area: snapshots;
	}
	#snapshot {
		grid-area: snapshot;
	}
	#graph {
		grid-area: graph;
	}
	.details {
		display: grid;
		grid-auto-flow: column;
		grid-template-rows: repeat(50, min-content); /* doesn't assume 3 defs but M<50 */
		position: relative;
		--horizontal-gap: var(--28, 1.75rem);
		gap: 0 var(--horizontal-gap);
	}
	dt {
		grid-row-start: 1; /* reset, next column */

		/* 14 Regular */
		font-size: 0.875rem;
		font-style: normal;
		font-weight: 400;
		line-height: 1.25rem; /* 142.857% */
		margin-bottom: var(--4, 0.25rem);
	}
	dd {
		margin: 0;

		/* 18 Semibold */
		font-size: 1.125rem;
		font-style: normal;
		font-weight: 600;
		line-height: 1.5rem; /* 133.333% */
	}

	dt:not(:first-child)::before {
		content: '';
		border-right: 1px solid var(--black-10, rgba(28, 28, 28, 0.1));
		position: absolute;
		height: 100%;
		transform: translateX(calc(-1 * var(--horizontal-gap) / 2));
	}
	.flex-column {
		flex-grow: 1;
		align-self: stretch;
		display: flex;
		flex-direction: column;
	}
	.info {
		width: 100%;
		display: flex;
		flex-direction: column;
	}
</style>
