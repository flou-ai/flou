<script lang="ts">
	import { PUBLIC_API_BASE_URL } from '$env/static/public';
	import Select from '$lib/UI/Select.svelte';
	import { tick } from 'svelte';
	import { FlowArrow } from 'phosphor-svelte';

	export let ltmId;
	export let state;
	export let disabled;
	export let cy;

	const emptyTransitionData = {
		label: '',
		params: '',
		payload: '',
		namespace: ''
	};
	let selectValue: any;
	let transitionData = { ...emptyTransitionData };

	let transitionOptions: any = [];

	const updateTransitions = async (cy) => {
		await tick();
		if (cy) {
			await tick();
			const activeNodes = cy.nodes().filter(function (ele) {
				return ele.data('status') === 'active';
			});
			transitionOptions = [];
			activeNodes.forEach((node: any) => {
				node.outgoers('edge[target]').forEach((edge: any) => {
					transitionOptions.push([
						{ label: edge.data('label'), namespace: edge.data('namespace') },
						edge.data('displayLabel')
					]);
				});
			});
		}
	};

	$: {
		state;
		updateTransitions(cy);
	}

	$: {
		if (selectValue) {
			transitionData.label = selectValue.label;
			transitionData.namespace = selectValue.namespace;
		} else {
			transitionData.label = '';
			transitionData.namespace = '';
		}
		if (!transitionData.label.includes('{')) {
			transitionData.params = '';
		}
	}

	let executeTransition = async (event: SubmitEvent) => {
		let url = `${PUBLIC_API_BASE_URL}ltm/${ltmId}/transition`;
		let postData: any = {
			transition: transitionData.label,
			namespace: transitionData.namespace
		};
		if (transitionData.payload) {
			postData['payload'] = JSON.parse(transitionData.payload);
		}
		if (transitionData.params) {
			postData['params'] = JSON.parse(transitionData.params);
		}
		transitionData = { ...emptyTransitionData };
		selectValue = null;

		await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(postData)
		})
			.then((response) => response.json())
			.then((data) => {
				// no need to update now we have ws
			})
			.catch((error) => {
				console.error('Error:', error);
			});
	};
</script>

<h3>Transition</h3>
<form on:submit|preventDefault={executeTransition}>
	<fieldset {disabled}>
		<Select
			bind:value={selectValue}
			options={transitionOptions}
			label="Transition"
			emptyLabel="Select Transition"
		/>
		{#if transitionData.label.includes('{')}
		<label>
			Params
			<textarea bind:value={transitionData.params} />
		</label>
		{/if}
		<label>
			Payload
			<textarea bind:value={transitionData.payload} />
		</label>
		<div class="buttons">
			<button type="submit" class="primary" disabled={!transitionData.label || disabled}>
				<FlowArrow size="1rem" />
				Execute Transition
			</button>
		</div>
	</fieldset>
</form>
