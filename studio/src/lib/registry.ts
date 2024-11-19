import { PUBLIC_API_BASE_URL } from '$env/static/public';

let registry: { name: string; fqn: string }[] | undefined;
const registryUrl = `${PUBLIC_API_BASE_URL}ltm/registry`;

export let getRegistry = async (fetch: any) => {
    await fetch(registryUrl)
        .then((response: any) => response.json())
        .then((data: any) => {
            registry = data;
            return data;
        })
        .catch((error: any) => {
            console.log(error);
            return [];
        });
    return registry?.map((item) => {
        return [item.fqn, item.name];
    })
};