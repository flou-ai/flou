import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';

import { PUBLIC_API_BASE_URL } from '$env/static/public';


export const load: PageLoad = async ({ fetch, params, url }) => {

    let ltm: any;
    let ltmUrl = `${PUBLIC_API_BASE_URL}ltm/${params.id}`;
    const rollbackIndex = url.searchParams.get('rollback');

    if (rollbackIndex) {
        ltmUrl += `?rollbacks=True`;
    }

    await fetch(ltmUrl)
        .then((response) => response.json())
        .then((data) => {
            ltm = data;
            console.log(ltm);
        })
        .catch((error) => {
            console.log(error);
            return [];
        });

    let rollback;
    if (rollbackIndex) {
        rollback = ltm.rollbacks[parseInt(rollbackIndex)];
        if (rollback) {
            ltm.state = rollback.state;
            ltm.snapshots = rollback.snapshots;
        } else {
            return error(404, 'Rollback not found');
        }
    }

    return { params, ltm, rollback }
};
export const ssr = false;