import type { PageLoad } from './$types';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';
import { PUBLIC_API_BASE_URL } from '$env/static/public';

let schemaOptions: [string, string][] = [];

const newDatasetInitial = {
    name: '',
    description: '',
    schema_fqn: ''
};

export const _newDatasetSchema = z.object({
    name: z.string(),
    description: z.string().optional(),
    schema_fqn: z.string()
}).refine((data) => {
    // If schema_fqn is empty string or undefined, it's valid
    if (!data.schema_fqn) return true;
    // Otherwise, it must be a valid schema FQN
    const validFQNs = schemaOptions.map(option => option[0]);
    return validFQNs.includes(data.schema_fqn);
}, {
    message: 'Invalid schema',
    path: ['schema_fqn']
});

export const load: PageLoad = async ({ fetch }) => {
    const response = await fetch(`${PUBLIC_API_BASE_URL}datasets/schemas`);
    const schemas = await response.json();
    schemaOptions = schemas.map((schema: any) => [
        schema.fqn,
        schema.name
    ]);

    const form = await superValidate(newDatasetInitial, zod(_newDatasetSchema));

    return { form, schemaOptions };
}; 