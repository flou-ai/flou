<script lang="ts">
	import { onMount } from 'svelte';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	export let ltmID: string;
	let socket: WebSocket;
	let retryCount = 0;
	const webSocketUrl = `${PUBLIC_API_BASE_URL}ws/${ltmID}`;

	onMount(() => {
		connectWebSocket();
	});

	const connectWebSocket = () => {
		socket = new WebSocket(webSocketUrl);
		socket.addEventListener('open', () => {
			// console.log('Opened');
			retryCount = 0;
		});
		socket.addEventListener('close', () => {
			attemptReconnect();
		});
		socket.addEventListener('error', () => {
			attemptReconnect();
		});
		socket.addEventListener('message', (event) => {
			console.log(event);
			let data = JSON.parse(event.data);
			if ('id' in data) {
				dispatch('update', data);
			}
		});
		// TODO: add reconnect
	};

	const attemptReconnect = () => {
		const delay = Math.min(1000 * Math.pow(2, retryCount), 30000);  // Exponential backoff
		setTimeout(() => {
			retryCount++;
			connectWebSocket();
		}, delay);
	}
</script>
