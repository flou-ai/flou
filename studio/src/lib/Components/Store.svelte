<script lang="ts">
	import { Camera } from 'phosphor-svelte';
	import { JsonView } from '@zerodevx/svelte-json-view';
	import SnapshotItem from './SnapshotItem.svelte';
	import Tabs from '../UI/Tabs.svelte';
	import Tab from '../UI/Tab.svelte';
	import LTMWidgets from './LTMWidgets.svelte';

	export let fullSnapshot: any = {};
	export let currentSnapshot: any = {};
	export let ltmId: string = '';
</script>

<h3><Camera size="1.25rem" />Store</h3>
{#if fullSnapshot.executeQueue?.length}
	<div>
		Pending Executions:
		<ul>
			{#each fullSnapshot.executeQueue as item}
				<li><SnapshotItem {item} /></li>
			{/each}
		</ul>
	</div>
{/if}
{#if fullSnapshot.transitionsQueue?.length}
	<div>
		Pending Transitions
		<ul>
			{#each fullSnapshot.transitionsQueue as item}
				<li><SnapshotItem {item} /></li>
			{/each}
		</ul>
	</div>
{/if}

<Tabs>
	<Tab title="Custom UI">
    <LTMWidgets {ltmId} store={fullSnapshot.store} />
  </Tab>
	<Tab title="Raw Store Diff">
		<JsonView json={currentSnapshot?.patch} />
	</Tab>
	<Tab title="Full Raw Store">
		<JsonView json={fullSnapshot.store} />
	</Tab>
</Tabs>
