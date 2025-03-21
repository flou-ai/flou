<script lang="ts">
  export let widget: any;
  export let data: any;
  
  // Extract configuration
  const { field, itemKey = null, itemTemplate = '{item}', title = 'List' } = widget;
  
  // Ensure data is an array
  $: items = Array.isArray(data) ? data : [];
  
  // Format item display using template
  function formatItem(item) {
    if (typeof item !== 'object' || item === null) {
      return String(item);
    }
    
    return itemTemplate.replace(/\{(\w+)\}/g, (match, key) => {
      return item[key] !== undefined ? String(item[key]) : match;
    });
  }
</script>

<div class="list-widget">
  <h3>{title}</h3>
  
  {#if items.length === 0}
    <div class="no-items">No items</div>
  {:else}
    <ul>
      {#each items as item}
        <li>
          {#if itemKey && typeof item === 'object' && item !== null}
            {formatItem(item)}
          {:else}
            {String(item)}
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .list-widget {
    padding: 1rem;
    border-radius: 0.5rem;
  }
  
  h3 {
    margin-top: 0;
    margin-bottom: 1rem;
  }
  
  .no-items {
    padding: 1rem;
    text-align: center;
    color: var(--gray-400);
  }
  
  ul {
    margin: 0;
    padding-left: 1.5rem;
  }
  
  li {
    margin-bottom: 0.5rem;
  }
  
  li:last-child {
    margin-bottom: 0;
  }
</style>