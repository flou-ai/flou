<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import { X } from 'phosphor-svelte';

    export let show = false;
    export let title = '';
    export let icon: any = undefined;

    const dispatch = createEventDispatcher();
    let dialog: HTMLDialogElement;

    const close = () => {
        dialog?.close();
        dispatch('close');
    };

    $: if (dialog) {
        if (show) {
            dialog.showModal();
        } else {
            dialog.close();
        }
    }

    // Close modal on escape key press (handled natively by dialog)
    const handleClose = (e: Event) => {
        if (e.target === dialog) {
            close();
        }
    };
</script>

<dialog class="dialog" bind:this={dialog} on:close={handleClose}>
    <div
        class="modal"
        on:click|self={handleClose}
        on:keydown|self={handleClose}
        role="button"
        tabindex="0"
    >
        <div class="modal-header">
            <div class="title-container">
                <h1>
                    {#if icon}
                        <svelte:component this={icon} size="3rem" />
                    {/if}
                    {title}
                </h1>
            </div>
            <button class="btn btn-primary close-button" on:click={close}>
                <X size="1.5rem" />
            </button>
        </div>
        <div class="modal-content">
            <slot />
        </div>
    </div>
</dialog>

<style lang="scss">
    dialog {
        padding: 0;
        border: none;
        background: transparent;

        &::backdrop {
            backdrop-filter: blur(20px);
            background: linear-gradient(
                180deg,
                rgba(215, 208, 255, 0.2) 0%,
                rgba(203, 221, 255, 0.3) 100%
            );
        }
    }

    .modal {
        max-width: 90vw;
        max-height: 90vh;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        width: 100%;
        color: var(--black-100);

        h1 {
            margin: 0;
        }

        .title-container {
            display: flex;
            align-items: center;
            gap: 0.5rem;

            .icon {
                display: flex;
                align-items: center;
            }
        }
    }

    .modal-content {
        border-radius: 2rem;
        width: fit-content;
        padding: 5rem;
        background: var(--primary-light);
        display: flex;
        flex-direction: column;
        gap: 1rem;
        position: relative;
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 2rem;
            background: var(--white-100);
            z-index: -1;
        }
    }

    .close-button {
        background: none;
        border: none;
        cursor: pointer;
        padding: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--black-100, #fff);

        border-radius: var(--12, 12px);
        background: var(--black-5, rgba(255, 255, 255, 0.1));

        &:hover {
            color: var(--primary);
        }
    }

    .modal-content :global(.button) {
        padding: 1rem 1.5rem;
    }
</style>
