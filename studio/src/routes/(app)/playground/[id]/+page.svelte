<script lang="ts">
    import { onMount } from 'svelte';
    import { invalidateAll } from '$app/navigation';
    import Block from '$lib/UI/Block.svelte';
    import LTMGraph from '$lib/UI/Graph/LTMGraph.svelte';
    import TransitionForm from '$lib/Components/TransitionForm.svelte';
    import SnapshotsTable from '$lib/Components/SnapshotsTable.svelte';
    import SnapshotNav from '$lib/Components/SnapshotNav.svelte';
    import Rollabacks from '$lib/Components/Rollbacks.svelte';
    import WebSocket from '$lib/WebSocket.svelte';
    import State from '$lib/Components/State.svelte';
    import { PUBLIC_API_BASE_URL } from '$env/static/public';
    import { TreeStructure } from 'phosphor-svelte';

    import type { PageData } from './$types';
    export let data: PageData;

    $: ({ ltm, params } = data);
    $: console.log(ltm);

    const ltmUrl = `${PUBLIC_API_BASE_URL}ltm/${data.params.id}`;
    let cy: any;

    ///// Snapshots management //////

    let snapshotIndex = 0;
    let snapshot: any = {};

    onMount(async () => {
        snapshotIndex = ltm.snapshots.length - 1;
    });

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
<div class="container">
    {#if ltm}
        <div id="title">
            <Block>
                <div class="info">
                    <h2><TreeStructure size="1.25rem" /> {ltm.name}</h2>
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
                        <dd>{ltm.created_at}</dd>
                        <dt>Updated At</dt>
                        <dd>{ltm.updated_at}</dd>
                    </dl>
                    <hr />
                    <TransitionForm
                        ltmId={params.id}
                        disabled={snapshotIndex !== ltm.snapshots.length - 1}
                        state={snapshot}
                        {cy}
                    />
                </div>
            </Block>
        </div>
        <div id="snapshots">
            <Block>
                <div>
                    <SnapshotsTable
                        {ltm}
                        ltmId={params.id}
                        bind:snapshot
                        bind:snapshotIndex
                        controls={true}
                        on:reloadLtm={invalidateAll}
                    />
                </div>
            </Block>
        </div>
        <div id="snapshot">
            <Block>
                <div>
                    <State fullSnapshot={snapshot} {currentSnapshot} />
                </div>
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
                        bind:cy
                    />
                </div>
            </Block>
        </div>
        <div id="rollbacks">
            <Block>
                <Rollabacks {ltm} ltmId={params.id} on:reloadLtm={invalidateAll} />
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
        grid-template-areas: 'title graph' 'snapshot snapshots' 'rollbacks rollbacks';
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
    #rollbacks {
        grid-area: rollbacks;
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
    .info {
        width: 100%;
        display: flex;
        flex-direction: column;
    }
    .flex-column {
        flex-grow: 1;
        align-self: stretch;
        display: flex;
        flex-direction: column;
    }
</style>
