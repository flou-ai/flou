import type { PageLoad } from './$types';

export const load: PageLoad = ({ params }) => {
    return params
};
export const ssr = false;