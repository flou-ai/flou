<script lang="ts">
	import { createEventDispatcher, tick } from 'svelte';
	import { Pencil, Check, X } from 'phosphor-svelte';
	import autosize from 'svelte-autosize';

	const dispatch = createEventDispatcher();
	export let value: string = '';

	let textarea: HTMLTextAreaElement;
	let isEditing = false;
	let currentText = value;

	let setEditing = async () => {
		isEditing = true;
		autosize.update(textarea);
		textarea.focus();
		textarea.selectionStart = textarea.selectionEnd = textarea.value.length;
	};

	let handleSave = () => {
		isEditing = false;
		value = currentText;
		dispatch('save', value);
	};

	let handleCancel = () => {
		isEditing = false;
		currentText = value;
		dispatch('cancel');
	};

	let handleKeyDown = (event: KeyboardEvent) => {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSave();
		} else if (event.key === 'Escape') {
			event.preventDefault();
			handleCancel();
		}
	};
</script>

<span class="container">
	<span
		class="plain-text {isEditing ? 'hidden' : 'visible'}"
		role="button"
		tabindex="0"
		on:click={setEditing}
		on:keydown={(e) => e.key === 'Enter' && setEditing()}
	>
		{currentText}
		<div class="actions plain {isEditing ? 'hidden' : 'visible'}">
			<span
				class="action"
				role="button"
				tabindex="0"
				on:click={setEditing}
				on:keydown={(e) => e.key === 'Enter' && setEditing()}
			>
				<Pencil size="1rem" />
				<!-- Pencil Icon -->
			</span>
		</div>
	</span>
	<div class="edit-text {isEditing ? 'visible' : 'hidden'}">
			<textarea
				bind:value={currentText}
				on:keydown={handleKeyDown}
				use:autosize
				bind:this={textarea}
				rows="1"
			></textarea>
		<div class="actions edit">
			<button
				class="save-icon"
				on:click={handleSave}
				on:keydown={(e) => e.key === 'Enter' && handleSave()}
			>
				<Check size="1rem" />
			</button>
			<button
				class="cancel-icon"
				on:click={handleCancel}
				on:keydown={(e) => e.key === 'Enter' && handleCancel()}
			>
				<X size="1rem" />
			</button>
		</div>
	</div>
</span>

<style lang="scss">
	:root {
		--displacement: 4px;
	}

	span {
		font-size: inherit;
		font-weight: inherit;
	}

	.container {
		position: relative;
		display: inline-block;
	}

	.visible {
		opacity: 1;
		z-index: 1;
	}

	.hidden {
		opacity: 0;
		z-index: 0;
		pointer-events: none;
	}

	.plain-text {
		display: inline-block;
	}
	.plain-text,
	.actions {
		white-space: pre-line;
		cursor: pointer;
	}

	.actions {
		position: absolute;
		right: 0;
		top: 0;
		display: flex;
		transition: opacity 0.2s;
		button {
			padding: 0.25rem;
		}
	}

	.plain {
		opacity: 0;
		transform: translateX(calc(100% + 0.25rem));
	}
	.edit {
		transform: translateY(calc(-100%)) translateX(calc(var(--displacement) * 2 + 1rem));
	}

	.container:hover .actions.plain {
		opacity: 1;
	}

	.edit-text {
		position: absolute;
		top: calc(-1 * var(--displacement));
		left: calc(-1 * var(--displacement));
		width: 100%;
		box-sizing: border-box;
	}

	textarea {
		margin: 0;
		width: 100%;
		padding-right: 1rem;
		border-radius: 0.5rem;
	}

	.save-icon {
		color: green;
		cursor: pointer;
	}

	.cancel-icon {
		color: red;
		cursor: pointer;
	}
</style>
