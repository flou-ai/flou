<script lang="ts">
	import { PUBLIC_API_BASE_URL } from '$env/static/public';
	import Select from '$lib/UI/Select.svelte';
	import { tick } from 'svelte';
	import { FlowArrow } from 'phosphor-svelte';

	export let ltmId;
	export let store;
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
	let selectedTransition: any = null;
	let schemaProperties: any[] = [];

	let transitionOptions: any = [];

	const updateTransitions = async (cy: any) => {
		await tick();
		if (cy) {
			await tick();
			const activeNodes = cy.nodes().filter(function (ele: any) {
				return ele.data('status') === 'active';
			});
			transitionOptions = [];
			activeNodes.forEach((node: any) => {
				node.outgoers('edge[target]').forEach((edge: any) => {
					transitionOptions.push([
						{ 
							label: edge.data('label'), 
							namespace: edge.data('namespace'),
							payload_schema: edge.data('payload_schema')
						},
						edge.data('displayLabel')
					]);
				});
			});
		}
	};

	$: {
		store;
		updateTransitions(cy);
	}

	// Transform JSON schema properties into form fields
	const formatSchemaProperties = (schema: any): any[] => {
		if (!schema || !schema.properties) return [];
		
		const properties: any[] = [];
		for (const [key, value] of Object.entries<any>(schema.properties)) {
			properties.push({
				name: key,
				type: value.type,
				description: value.description || '',
				required: schema.required?.includes(key) || false,
				value: null,
			});
		}
		return properties;
	};

	$: {
		if (selectValue) {
			transitionData.label = selectValue.label;
			transitionData.namespace = selectValue.namespace;
			selectedTransition = selectValue;
			schemaProperties = selectValue.payload_schema ? 
				formatSchemaProperties(selectValue.payload_schema) : [];
		} else {
			transitionData.label = '';
			transitionData.namespace = '';
			selectedTransition = null;
			schemaProperties = [];
		}
		if (!transitionData.label.includes('{')) {
			transitionData.params = '';
		}
	}
	
	// Update payload before submitting form
	const updatePayloadFromSchema = () => {
		if (!schemaProperties.length) return;
		
		const payloadData: Record<string, any> = {};
		schemaProperties.forEach(prop => {
			payloadData[prop.name] = prop.value;
		});
		
		transitionData.payload = JSON.stringify(payloadData, null, 2);
	};

	// Make schema properties reactive
	const updateSchemaPropertyValue = (index: number, value: any) => {
		schemaProperties = [
			...schemaProperties.slice(0, index),
			{ ...schemaProperties[index], value },
			...schemaProperties.slice(index + 1)
		];
	};

	let executeTransition = async (event: SubmitEvent) => {
		let url = `${PUBLIC_API_BASE_URL}ltm/${ltmId}/transition`;
		let postData: any = {
			transition: transitionData.label,
			namespace: transitionData.namespace
		};
		
		// Generate payload from form fields if using schema
		if (schemaProperties.length) {
			updatePayloadFromSchema();
		}
		
		if (transitionData.payload) {
			try {
				postData['payload'] = JSON.parse(transitionData.payload);
			} catch (error) {
				console.error('Invalid JSON payload:', error);
				return;
			}
		}
		
		if (transitionData.params) {
			try {
				postData['params'] = JSON.parse(transitionData.params);
			} catch (error) {
				console.error('Invalid JSON params:', error);
				return;
			}
		}
		
		transitionData = { ...emptyTransitionData };
		selectValue = null;
		schemaProperties = [];

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
			ariaInvalid={false}
		/>
		
		{#if transitionData.label.includes('{')}
		<label>
			Params
			<textarea bind:value={transitionData.params} />
		</label>
		{/if}
		
		{#if schemaProperties.length > 0}
			<div class="schema-form">
				<h4>Payload Form</h4>
				{#each schemaProperties as prop, index}
					<div class="form-field">
						<label>
							{prop.name}
							{#if prop.required}<span class="required">*</span>{/if}
							{#if prop.description}<span class="description">{prop.description}</span>{/if}
							
							{#if prop.type === 'string'}
								<input
									type="text"
									value={prop.value || ''}
									on:input={(e) => updateSchemaPropertyValue(index, e.target.value)}
									required={prop.required}
								/>
							{:else if prop.type === 'number' || prop.type === 'integer'}
								<input
									type="number"
									value={prop.value || ''}
									on:input={(e) => updateSchemaPropertyValue(index, e.target.valueAsNumber)}
									required={prop.required}
									step={prop.type === 'integer' ? 1 : 'any'}
								/>
							{:else if prop.type === 'boolean'}
								<input
									type="checkbox"
									checked={prop.value || false}
									on:change={(e) => updateSchemaPropertyValue(index, e.target.checked)}
								/>
							{/if}
						</label>
					</div>
				{/each}
			</div>
		{:else}
			<label>
				Payload (JSON)
				<textarea bind:value={transitionData.payload} />
			</label>
		{/if}
		
		<div class="buttons">
			<button type="submit" class="primary" disabled={!transitionData.label || disabled}>
				<FlowArrow size="1rem" />
				Execute Transition
			</button>
		</div>
	</fieldset>
</form>

<style>
	textarea {
		width: 100%;
		height: 80px;
		font-family: monospace;
		resize: vertical;
	}

	h3 {
		margin-bottom: 1rem;
	}

	.buttons {
		margin-top: 1rem;
		display: flex;
		justify-content: flex-end;
	}

	button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	form {
		margin-bottom: 1rem;
	}

	label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 500;
	}

	fieldset {
		border: none;
		padding: 0;
		margin: 0;
	}

	.schema-form {
		margin-top: 1rem;
		border: 1px solid var(--black-20);
		border-radius: 4px;
		padding: 1rem;
		background-color: var(--black-5);
	}

	.schema-form h4 {
		margin-top: 0;
		margin-bottom: 1rem;
		font-size: 1rem;
	}

	.form-field {
		margin-bottom: 1rem;
	}

	.form-field:last-child {
		margin-bottom: 0;
	}

	.form-field input[type="text"],
	.form-field input[type="number"] {
		width: 100%;
		padding: 0.5rem;
		border: 1px solid var(--black-20);
		border-radius: 4px;
	}

	.required {
		color: var(--secondary-red);
		margin-left: 0.25rem;
	}

	.description {
		display: block;
		font-size: 0.875rem;
		color: var(--black-60);
		font-weight: normal;
		margin-bottom: 0.5rem;
	}
</style>