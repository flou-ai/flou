import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';

import { getRegistry } from '$lib/registry';

let registryOptions: any = [];

const newExperimentInitial = {
    name: '',
    description: '',
    trial: {
        name: 'First Trial',
        fqn: '',
    }
};

export const _newExperimentSchema = z.object({
    name: z.string(),
    description: z.string(),
    trial: z.object({
        name: z.string().default('First Trial'),
        fqn: z.string()
    })
    .refine((data) => {
        const validFQNs = registryOptions.map((option: any) => option[0]);
        console.log('here', data, validFQNs, registryOptions);
        return validFQNs.includes(data.fqn);
    }, {
        message: 'Invalid LTM',
        path: ['trial', 'fqn']
    })
});

export const load: PageLoad = async ({ params, fetch }) => {

    registryOptions = await getRegistry();

    const form = await superValidate(newExperimentInitial, zod(_newExperimentSchema));

    return { form, registryOptions };
};