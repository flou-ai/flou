<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';
	import Block from '$lib/UI/Block.svelte';
	import { superForm } from 'sveltekit-superforms';
	import { zod } from 'sveltekit-superforms/adapters';
	import type { PageData } from './$types';

	export let data: PageData;
	const { dataset } = data;

	type SchemaProperty = {
		name: string;
		type: string;
		required: boolean;
		stringValue: string;
		numberValue: number;
		booleanValue: boolean;
	};

	interface JsonSchemaProperty {
		type: string;
		[key: string]: any;
	}

	// Helper function to format schema properties for display and form generation
	const formatSchemaProperties = (schema: any): SchemaProperty[] => {
		const properties: SchemaProperty[] = [];
		for (const [key, value] of Object.entries<JsonSchemaProperty>(schema.properties)) {
			if (key === 'name') continue; // Skip base model fields
			properties.push({
				name: key,
				type: value.type,
				required: true,
				stringValue: '',
				numberValue: 0,
				booleanValue: false
			});
		}
		return properties;
	};

	const schemaProperties = formatSchemaProperties(dataset.json_schema);
	
	// Create a form data object from schema properties
	const createFormData = () => {
		const formData: Record<string, any> = {};
		schemaProperties.forEach(prop => {
			formData[prop.name] = prop.type === 'string' 
				? prop.stringValue 
				: prop.type === 'boolean' 
					? prop.booleanValue 
					: prop.numberValue;
		});
		return { data: JSON.stringify(formData, null, 2) };
	};

	const { form, errors, message, enhance } = superForm(data.form, {
		SPA: true,
		dataType: 'json',
		onUpdate({ form }) {
			if (form.valid && typeof form.data === 'string') {
				handleSubmit({ data: form.data });
			}
		}
	});

	// Update the JSON data when form fields change
	const updateFormData = () => {
		const formData: Record<string, any> = {};
		schemaProperties.forEach(prop => {
			formData[prop.name] = prop.type === 'string' 
				? prop.stringValue 
				: prop.type === 'boolean' 
					? prop.booleanValue 
					: prop.numberValue;
		});
		$form.data = JSON.stringify(formData, null, 2);
	};

	const handleSubmit = async (formData: { data: string }) => {
		try {
			const response = await fetch(`${PUBLIC_API_BASE_URL}datasets/${dataset.id}/items`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					data: JSON.parse(formData.data)
				})
			});

			if (!response.ok) {
				throw new Error('Failed to create item');
			}

			goto(`/datasets/${dataset.id}`);
		} catch (err) {
			console.error('Error:', err);
			return {
				message: err instanceof SyntaxError ? 'Invalid JSON data' : 'Failed to create item'
			};
		}
	};
</script>

<div class="table-header">
	<h2>Add Item to Dataset</h2>
	<div class="table-controls">
		<a href="/datasets/{dataset.id}" class="button secondary">Back to Dataset</a>
	</div>
</div>

<Block>
	{#if $message}<div class="error">{$message}</div>{/if}
	<form use:enhance>
		<p>Add a new item to dataset: <strong>{dataset.name}</strong></p>

		{#if dataset.schema_fqn}
			<p>This dataset uses schema: <code>{dataset.schema_fqn}</code></p>
		{/if}

		<div class="form-fields">
			{#each schemaProperties as prop}
				<div class="form-field">
					<label>
						{prop.name}
						{#if prop.required}<span class="required">*</span>{/if}
						<br />
						<span class="field-type">Type: <code>{prop.type}</code></span>
						{#if prop.type === 'string'}
							<input
								type="text"
								bind:value={prop.stringValue}
								on:input={updateFormData}
								required={prop.required}
							/>
						{:else if prop.type === 'number' || prop.type === 'integer'}
							<input
								type="number"
								bind:value={prop.numberValue}
								on:input={updateFormData}
								required={prop.required}
								step={prop.type === 'integer' ? 1 : 'any'}
							/>
						{:else if prop.type === 'boolean'}
							<input
								type="checkbox"
								bind:checked={prop.booleanValue}
								on:change={updateFormData}
							/>
						{/if}
					</label>
				</div>
			{/each}
		</div>

		<div class="json-preview">
			<h3>JSON Preview</h3>
			<pre>{$form.data}</pre>
		</div>

		<div class="buttons">
			<a href="/datasets/{dataset.id}" class="button secondary">Cancel</a>
			<button type="submit" class="button primary">Add Item</button>
		</div>
	</form>
</Block>

<style lang="scss">
	.error {
		color: var(--secondary-red);
		margin-bottom: 1rem;
		padding: 0.5rem;
		border: 1px solid var(--secondary-red);
		border-radius: 0.25rem;
		background-color: var(--black-5);
	}

	.invalid {
		color: var(--secondary-red);
		font-size: 0.875rem;
	}

	.form-fields {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		margin-bottom: 2rem;
	}

	.form-field {
		label {
			display: block;
			font-weight: 500;

			.required {
				color: var(--secondary-red);
				margin-left: 0.25rem;
			}

			.field-type {
				display: block;
				font-size: 0.875rem;
				color: var(--black-60);
				margin-bottom: 0.5rem;
			}

			input[type="text"],
			input[type="number"] {
				width: 100%;
				padding: 0.5rem;
				border: 1px solid var(--black-20);
				border-radius: 0.25rem;
				background-color: var(--primary-background);
				color: var(--black-100);
				font-family: inherit;

				&:focus {
					outline: none;
					border-color: var(--logo-color-logo);
				}

				&[aria-invalid="true"] {
					border-color: var(--secondary-red);
				}
			}

			input[type="checkbox"] {
				margin-top: 0.5rem;
			}
		}
	}

	.json-preview {
		margin: 1rem 0;
		padding: 1rem;
		background-color: var(--black-5);
		border-radius: 0.25rem;

		h3 {
			margin: 0 0 1rem 0;
			font-size: 1rem;
			color: var(--black-60);
		}

		pre {
			margin: 0;
			padding: 1rem;
			background-color: var(--primary-background);
			border-radius: 0.25rem;
			font-family: monospace;
			font-size: 0.875rem;
			overflow-x: auto;
		}
	}

	code {
		background-color: var(--black-5);
		padding: 0.125rem 0.25rem;
		border-radius: 0.25rem;
		font-family: monospace;
	}

	.buttons {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
		margin-top: 1rem;
	}

	.button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		border-radius: 0.25rem;
		font-weight: 500;
		cursor: pointer;
		text-decoration: none;
		border: none;

		&.primary {
			background-color: var(--logo-color-logo);
			color: var(--white-100);

			&:hover {
				background-color: var(--logo-color-logo-2);
			}
		}

		&.secondary {
			background-color: var(--primary-light);
			color: var(--black-100);

			&:hover {
				background-color: var(--black-10);
			}
		}
	}
</style> 