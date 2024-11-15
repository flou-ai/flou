<script lang="ts">
    import { ClockCounterClockwise, Lifebuoy, TestTube } from 'phosphor-svelte';
    import { createEventDispatcher } from 'svelte';

    import Paginator from '$lib/UI/Paginator.svelte';
    import SnapshotItem from '$lib/Components/SnapshotItem.svelte';
    import { formatDate } from '$lib/utils';
    import { PUBLIC_API_BASE_URL } from '$env/static/public';
    import NewTrialFromRollback from '$lib/Components/NewTrialFromRollback.svelte';

    let dispatch = createEventDispatcher();

    export let ltm: any;
    export let ltmId;
    export let experiment: any;
    let index = 0;
    let showTrialModal = false;
    let selectedAction = 'recover-rollback';
    let selectedIndex = 0;

    const ltmUrl = `${PUBLIC_API_BASE_URL}ltm/${ltmId}`;

    let recoverRollback = async (rollbackIndex: number, newTrialData: any = undefined) => {
        let postData: any = {
            rollback: {
                index: rollbackIndex
            }
        };
        console.log('NEW TRIAL DATA');
        console.log(newTrialData);
        if (newTrialData) {
            postData['new_trial'] = newTrialData;
        }
        await fetch(`${ltmUrl}/rollback`, {
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
        <th>
            {#if experiment}
                <span class="th-icon">New trial <TestTube /></span>
            {/if}
        </th>
    </tr>
    {#each ltm.rollbacks as rollback, i}
        {@const lastSnapshot = rollback.snapshots.at(-1)}
        <tr
            class:current={i === index}
            on:click={() => (index = i)}
            on:keydown={() => (index = i)}
            role="button"
        >
            <td title={rollback.reason}>{rollback.reason}</td>
            <td title={rollback.snapshots.length}>{rollback.snapshots.length}</td>
            <td title={`${lastSnapshot.reason}`}
                >{lastSnapshot.reason}: <SnapshotItem item={lastSnapshot.item} />
            </td><td title={formatDate(rollback.time)}>{formatDate(rollback.time)}</td>
            <td>
                <div class="snapshot-controls">
                    {#if experiment}
                        <button
                            on:click={() => {
                                selectedIndex = i;
                                showTrialModal = true;
                            }}
                            title="Recover rollback"
                        >
                            <Lifebuoy size="1.25rem" />
                        </button>
                    {:else}
                        <button
                            on:click={() => {
                                recoverRollback(i);
                            }}
                            title="Recover rollback"
                        >
                            <Lifebuoy size="1.25rem" />
                        </button>
                    {/if}
                </div>
            </td>
        </tr>{/each}
</table>
<Paginator bind:index collection={ltm.rollbacks} />

{#if experiment}
    <NewTrialFromRollback
        bind:showTrialModal
        bind:selectedIndex
        bind:ltm
        selectedAction="recover-rollback"
        on:newTrial={(event) => {
            recoverRollback(event.detail.index, event.detail.newTrialData);
        }}
    />
{/if}
