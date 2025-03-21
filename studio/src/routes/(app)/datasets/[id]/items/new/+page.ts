import type { PageLoad } from './$types';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';
import { PUBLIC_API_BASE_URL } from '$env/static/public';

// We'll create the schema after fetching the dataset
const createItemSchema = (jsonSchema: any) => {
    // Convert JSON Schema to Zod schema
    const zodSchema = z.object({
        data: z.string().default('{}')
    });
    return zodSchema;
};

export const load: PageLoad = async ({ params, fetch }) => {
    // Fetch the dataset to get its schema
    const response = await fetch(`${PUBLIC_API_BASE_URL}datasets/${params.id}`);
    if (!response.ok) {
        throw new Error('Failed to load dataset');
    }
    const dataset = await response.json();
    
    // Create the schema based on the dataset's JSON schema
    const schema = createItemSchema(dataset.json_schema);
    
    // Initialize the form with the schema
    const form = await superValidate(zod(schema));
    
    return { form, dataset };
};

export const ssr = false; 