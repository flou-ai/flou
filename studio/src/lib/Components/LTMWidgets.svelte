<script lang="ts">
  import { onMount } from 'svelte';
  import { PUBLIC_API_BASE_URL } from '$env/static/public';
  import WidgetRenderer from '../widgets/WidgetRenderer.svelte';
  import { writable } from 'svelte/store';
  import '../widgets'; // Import to register widgets
  
  export let ltmId: string;
  export let state: any;
  
  // Store for UI schema
  const uiSchema = writable<any>({});
  let loading = true;
  let error = null;
  
  // Load UI schema on mount 
  onMount(async () => {
    try {
      const response = await fetch(`${PUBLIC_API_BASE_URL}ltm/${ltmId}/ui`);
      if (!response.ok) throw new Error('Failed to load UI schema');
      
      const schema = await response.json();
      uiSchema.set(schema);
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  });
</script>

{#if loading}
  <p>Loading widgets...</p>
{:else if error}
  <p class="error">Error: {error}</p>
{:else}
  <div class="ltm-widgets">
    {#each $uiSchema.widgets || [] as widget}
      <div class="widget-container">
        <WidgetRenderer 
          {widget} 
          data={widget.field ? state[widget.field] : state} 
          {ltmId} 
        />
      </div>
    {/each}
  </div>
{/if}

<style>
  .ltm-widgets {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--20, 1.25rem);
  }
  
  .widget-container {
    background: var(--white);
    border-radius: var(--8);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
  }
  
  .error {
    color: var(--red);
  }
</style>