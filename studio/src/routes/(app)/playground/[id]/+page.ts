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


    return { params, ltm: await ltm }
};
export const ssr = false;