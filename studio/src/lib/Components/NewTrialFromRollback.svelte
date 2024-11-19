<script lang="ts">
    import Modal from '$lib/UI/Modal.svelte';
    import { Plus, TestTube } from 'phosphor-svelte';
    import SnapshotItem from '$lib/Components/SnapshotItem.svelte';

    import { superForm, defaults } from 'sveltekit-superforms';
    import { zod } from 'sveltekit-superforms/adapters';
    import { z } from 'zod';
    import { createEventDispatcher } from 'svelte';

    let dispatch = createEventDispatcher();

    export const _newTrialSchema = z.object({
        name: z.string().optional(),
        previous_trial_outputs: z.string().optional(),
        outputs: z.string().optional()
    });

    export let showTrialModal = false;
    export let selectedAction: 'rollback' | 'replay' | 'recover-rollback' = 'rollback';
    export let selectedIndex: number;
    export let ltm: any = {};

    const { form, errors, message, constraints, enhance } = superForm(
        defaults(zod(_newTrialSchema)),
        {
            SPA: true,
            dataType: 'json',
            validators: zod(_newTrialSchema),
            onUpdate({ form }) {
                if (form.valid) {
                    showTrialModal = false;
                    dispatch('newTrial', {
                        index: selectedIndex,
                        replay: selectedAction === 'replay',
                        newTrialData: form.data
                    });
                }
            }
        }
    );
</script>

<Modal
    bind:show={showTrialModal}
    title={`New Trial`}
    icon={Plus}
    on:close={() => (showTrialModal = false)}
>
    <div class="modal-header">
        <div class="icon-container">
            <TestTube size="2.5rem" />
        </div>
        <div>
            {#if showTrialModal}
                {#if selectedAction === 'recover-rollback'}
                    {@const lastSnapshot = ltm.rollbacks[selectedIndex].snapshots.at(-1)}

                    Recover Rollback #{selectedIndex}
                    <div class="snapshot-item">
                        Last Snapshot
                        <SnapshotItem item={lastSnapshot.item}></SnapshotItem>
                    </div>
                {:else}
                    {#if selectedAction === 'rollback'}
                        Rollback
                    {:else}
                        Replay
                    {/if}
                    from snapshot #{selectedIndex}
                    <div class="snapshot-item">
                        {#if ltm.snapshots[selectedIndex]}
                            <SnapshotItem item={ltm.snapshots[selectedIndex].item}></SnapshotItem>
                        {/if}
                    </div>
                {/if}
            {/if}
        </div>
    </div>
    {#if $form}
        <form use:enhance>
            <label>
                Name
                <input
                    aria-invalid={$errors.name ? 'true' : undefined}
                    type="text"
                    bind:value={$form.name}
                    {...$constraints.name}
                    placeholder={`${ltm.current_trial?.name} #${ltm.current_trial?.index + 1}`}
                />
            </label>
            <label>
                Previous trial results
                <textarea
                    aria-invalid={$errors.previous_trial_outputs ? 'true' : undefined}
                    bind:value={$form.previous_trial_outputs}
                    {...$constraints.previous_trial_outputs}
                />
            </label>
            <label>
                New trial description
                <textarea
                    aria-invalid={$errors.outputs ? 'true' : undefined}
                    bind:value={$form.outputs}
                    {...$constraints.outputs}
                />
            </label>
            <div class="buttons full-width">
                <button
                    type="button"
                    class="button large secondary"
                    on:click={() => (showTrialModal = false)}
                >
                    Cancel
                </button>
                <button type="submit" class="button primary large"> Create Trial </button>
            </div>
        </form>
    {/if}
</Modal>

<style lang="scss">
    .icon-container {
        padding: 1.25rem;
        border-radius: 100%;
        background-color: var(--black-5);
        max-width: fit-content;
        aspect-ratio: 1 / 1;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--black-100);
    }
    .modal-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        color: var(--black-100);
    }
    .snapshot-item {
        margin-top: 0.5rem;
        font-size: 0.875rem;
        overflow: auto;
        text-overflow: ellipsis;
    }
</style>
