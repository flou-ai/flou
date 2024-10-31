<script lang="ts">
	import { onMount } from 'svelte';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	export let ltmID: string;
	let socket: WebSocket;
	const webSocketUrl = `${PUBLIC_API_BASE_URL}ws/${ltmID}`;

	onMount(() => {
		socket = new WebSocket(webSocketUrl);
		socket.addEventListener('open', () => {
			// console.log('Opened');
		});
		socket.addEventListener('message', (event) => {
			console.log(event);
			let data = JSON.parse(event.data);
			if ('id' in data) {
				dispatch('update', data);
			}
		});
		// TODO: add reconnect
	});
</script>
