import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';
import { PUBLIC_API_BASE_URL } from '$env/static/public';
import { getRegistry } from '$lib/registry';

let registryOptions: any = [];

const newTrialInitial = {
    name: 'Trial',
    fqn: undefined,
};

export const _newTrialSchema = z.object({
    name: z.string().default('Trial'),
    fqn: z.string()
    .refine((data: any) => {
        const validFQNs = registryOptions.map((option: any) => option[0]);
        return validFQNs.includes(data);
    }, {
        message: 'Invalid LTM',
    }),
    inputs: z.string().optional()
});

export const load: PageLoad = async ({ params, fetch }) => {

    const experiment =  fetch(`${PUBLIC_API_BASE_URL}experiments/${params.id}`)
        .then((response) => response.json())
        .catch((error) => {
            console.log(error);
            return [];
        });
    registryOptions = await getRegistry(fetch);

    const form = await superValidate(newTrialInitial, zod(_newTrialSchema));

    return { form, registryOptions, params, experiment: await experiment };
};