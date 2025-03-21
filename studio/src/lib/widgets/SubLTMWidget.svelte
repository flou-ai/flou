<script lang="ts">
  import { goto } from '$app/navigation';
  
  export let widget: any;
  export let data: any;
  export let ltmId: string;
  
  // Extract configuration
  const { pattern, display = 'inline', maxItems = null, title = 'Nested LTMs' } = widget;
  
  // Function to extract instance names from pattern
  function getInstanceNames() {
    const matches = [];
    const regex = new RegExp(pattern.replace(/\{(\w+)\}/g, '(.+)'));
    
    for (const key in data) {
      const match = key.match(regex);
      if (match) {
        matches.push({ 
          key,
          value: data[key]
        });
      }
    }
    
    // Apply maxItems limit if provided
    return maxItems ? matches.slice(0, maxItems) : matches;
  }
  
  $: instances = getInstanceNames();
  
  function navigateToLTM(key) {
    // This would need to be updated based on your app's routing structure
    goto(`/ltm/${ltmId}/${key}`);
  }
</script>

<div class="subltm-widget">
  <h3>{title}</h3>
  
  {#if instances.length === 0}
    <div class="no-instances">No instances found</div>
  {:else}
    <div class="instances {display}">
      {#each instances as instance}
        <div class="instance">
          {#if display === 'link'}
            <button class="link" on:click={() => navigateToLTM(instance.key)}>
              {instance.key}
            </button>
          {:else if display === 'inline'}
            <details>
              <summary>{instance.key}</summary>
              <div class="instance-content">
                <pre>{JSON.stringify(instance.value, null, 2)}</pre>
              </div>
            </details>
          {:else if display === 'modal'}
            <button on:click={() => /* Show modal logic */ null}>
              {instance.key}
            </button>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .subltm-widget {
    padding: 1rem;
    border-radius: 0.5rem;
  }
  
  h3 {
    margin-top: 0;
    margin-bottom: 1rem;
  }
  
  .no-instances {
    padding: 1rem;
    text-align: center;
    color: var(--gray-400);
  }
  
  .instances {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .instance {
    border: 1px solid var(--gray-200);
    border-radius: 0.25rem;
    overflow: hidden;
  }
  
  summary {
    padding: 0.75rem;
    cursor: pointer;
    font-weight: 500;
    background: var(--gray-50);
  }
  
  summary:hover {
    background: var(--gray-100);
  }
  
  .instance-content {
    padding: 0.75rem;
  }
  
  pre {
    margin: 0;
    background: var(--gray-50);
    padding: 0.5rem;
    border-radius: 0.25rem;
    max-height: 300px;
    overflow: auto;
    font-size: 0.875rem;
  }
  
  button.link {
    background: none;
    border: none;
    padding: 0.75rem;
    width: 100%;
    text-align: left;
    font-weight: 500;
    cursor: pointer;
    color: var(--blue-600);
  }
  
  button.link:hover {
    background: var(--blue-50);
  }
</style>