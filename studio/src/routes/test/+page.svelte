<script lang="ts">
	import { onMount } from 'svelte';
	import LTMGraph from '$lib/UI/Graph/LTMGraph.svelte';

	const structure = {
		name: 'nested',
		fqn: 'nested',
		ltms: [
			{
				name: 'linear',
				fqn: 'nested.linear',
				ltms: [
					{
						name: 'end',
						fqn: 'nested.linear.end'
					},
					{
						name: 'start',
						fqn: 'nested.linear.start',
						init: ['one'],
						ltms: [
							{
								name: 'one',
								fqn: 'nested.linear.start.one'
							},
							{
								name: 'two',
								fqn: 'nested.linear.start.two'
							}
						]
					}
				],
				init: ['start'],
				transitions: [
					{
						from: 'start',
						to: 'end',
						label: 'go'
					}
				]
			},
			{
				name: 'linear2',
				fqn: 'nested.linear2',
				ltms: [
					{
						name: 'end',
						fqn: 'nested.linear2.end'
					},
					{
						name: 'start',
						fqn: 'nested.linear2.start'
					}
				],
				init: ['start'],
				transitions: [
					{
						from: 'start',
						to: 'end',
						label: 'go'
					}
				]
			},
			{
				name: 'start',
				fqn: 'nested.start'
			}
		],
		init: ['start'],
		transitions: [
			{
				from: 'start',
				to: 'linear',
				label: 'go'
			}
		]
	};
</script>

<LTMGraph ltm={structure} />

<style lang="scss">
</style>
