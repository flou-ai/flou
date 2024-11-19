import type { PageLoad } from './$types';
import { PUBLIC_API_BASE_URL } from '$env/static/public';

export const load: PageLoad = async ({ fetch, params }) => {
    const { id } = params;

    let experiment: any;
    await fetch(`${PUBLIC_API_BASE_URL}experiments/${id}`)
        .then((response) => response.json())
        .then((data) => {
            experiment = data;
        })
        .catch((error) => {
            console.log(error);
            return [];
        });

    return {...params, experiment}
};
export const ssr = false;