import { PUBLIC_API_BASE_URL } from '$env/static/public';

let registry: { name: string; fqn: string }[] | undefined;
const registryUrl = `${PUBLIC_API_BASE_URL}ltm/registry`;

export let getRegistry = async () => {
    await fetch(registryUrl)
        .then((response) => response.json())
        .then((data) => {
            registry = data;
        })
        .catch((error) => {
            console.log(error);
            return [];
        });
    return registry?.map((item) => {
        return [item.fqn, item.name];
    })
};