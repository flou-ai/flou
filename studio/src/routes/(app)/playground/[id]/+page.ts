import type { PageLoad } from './$types';
import { PUBLIC_API_BASE_URL } from '$env/static/public';

export const load: PageLoad = async ({ fetch, params }) => {

    let ltmUrl = `${PUBLIC_API_BASE_URL}ltm/${params.id}?rollbacks=True`;

    const ltm = fetch(ltmUrl)
        .then((response) => response.json())
        .then((data) => {
            console.log(ltm);
            return data;
        })
        .catch((error) => {
            console.log(error);
            return [];
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

    return {
        params,
        ltm: await ltm,
        experiment: await experiment
    }

};
export const ssr = false;