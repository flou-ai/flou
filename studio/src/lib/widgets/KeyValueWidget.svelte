<script lang="ts">
  export let widget: any;
  export let data: any;
  
  // Extract configuration
  const { field = null, keys = null, excludeKeys = [], title = 'Details' } = widget;
  
  // Get data to display
  $: dataToDisplay = field ? data[field] : data;
  
  // Filter keys to show 
  $: entries = Object.entries(dataToDisplay || {})
    .filter(([key]) => {
      // If specific keys are provided, only show those
      if (keys && Array.isArray(keys)) {
        return keys.includes(key);
      }
      // Otherwise show all keys except excluded ones and keys starting with _
      return !excludeKeys.includes(key) && !key.startsWith('_');
    });
</script>

<div class="key-value-widget">
  <h3>{title}</h3>
  
  {#if !dataToDisplay || entries.length === 0}
    <div class="no-data">No data available</div>
  {:else}
    <dl>
      {#each entries as [key, value]}
        <div class="item">
          <dt>{key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')}</dt>
          <dd>
            {#if typeof value === 'object' && value !== null}
              <details>
                <summary>Object</summary>
                <pre>{JSON.stringify(value, null, 2)}</pre>
              </details>
            {:else if typeof value === 'boolean'}
              {value ? 'Yes' : 'No'}
            {:else}
              {value}
            {/if}
          </dd>
        </div>
      {/each}
    </dl>
  {/if}
</div>

<style>
  .key-value-widget {
    padding: 1rem;
    border-radius: 0.5rem;
  }
  
  h3 {
    margin-top: 0;
    margin-bottom: 1rem;
  }
  
  .no-data {
    padding: 1rem;
    text-align: center;
    color: var(--gray-400);
  }
  
  dl {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1rem;
    margin: 0;
  }
  
  .item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  dt {
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--gray-600);
  }
  
  dd {
    margin: 0;
    font-size: 1rem;
  }
  
  details {
    cursor: pointer;
  }
  
  summary {
    font-weight: 500;
    margin-bottom: 0.25rem;
  }
  
  pre {
    background: var(--gray-50);
    padding: 0.5rem;
    border-radius: 0.25rem;
    max-height: 200px;
    overflow: auto;
    font-size: 0.875rem;
  }
</style>