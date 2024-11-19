import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';

import { PUBLIC_API_BASE_URL } from '$env/static/public';


export const load: PageLoad = async ({ fetch, params, url }) => {

    let ltmUrl = `${PUBLIC_API_BASE_URL}ltm/${params.id}`;
    const rollbackIndex = url.searchParams.get('rollback');

    if (rollbackIndex) {
        ltmUrl += `?rollbacks=True`;
    }

    const ltm = fetch(ltmUrl)
        .then((response) => response.json())
        .then((data) => {
            return data;
        })
        .catch((error) => {
            console.log(error);
            return [];
        });

    const rollback = ltm.then((ltmData: any) => {
        console.log(ltmData)
        if (rollbackIndex) {
            const rollback = ltmData.rollbacks[parseInt(rollbackIndex)];
            if (rollback) {
                ltmData.state = rollback.state;
                ltmData.snapshots = rollback.snapshots;
                return rollback;
            } else {
                return error(404, 'Rollback not found');
            }
        }

    });

    const experiment = ltm.then(ltmData => {
        if (ltmData.experiment_id) {
            return fetch(`${PUBLIC_API_BASE_URL}experiments/${ltmData.experiment_id}`)
                .then((response) => response.json())
                .then((data) => {
                    return data;
                })
                .catch((error) => {
                    console.log(error);
                    return null;
                });
        }
        return null;
    });


    console.log(params)
    return { params, ltm: await ltm, rollback: await rollback, experiment: await experiment }
};
export const ssr = false;