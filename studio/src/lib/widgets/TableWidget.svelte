<script lang="ts">
  export let widget: any;
  export let data: any;
  
  // Extract configuration from widget
  const { columns = [], sortable = true, filterable = false, title = 'Table' } = widget;
  
  // Ensure data is an array
  $: items = Array.isArray(data) ? data : [];
  
  // Sort state
  let sortColumn = '';
  let sortDirection = 'asc';
  
  // Filter state
  let filterText = '';
  
  // Process columns
  $: processedColumns = columns.map(col => {
    if (typeof col === 'string') {
      return {
        key: col,
        label: col.charAt(0).toUpperCase() + col.slice(1).replace(/_/g, ' ')
      };
    }
    return col;
  });
  
  // Filter items based on filterText
  $: filteredItems = filterText && filterable 
    ? items.filter(item => 
        processedColumns.some(col => 
          String(item[col.key]).toLowerCase().includes(filterText.toLowerCase())
        )
      )
    : items;
  
  // Sort items based on sortColumn and sortDirection
  $: sortedItems = sortColumn && sortable
    ? [...filteredItems].sort((a, b) => {
        const valueA = a[sortColumn];
        const valueB = b[sortColumn];
        
        if (typeof valueA === 'string' && typeof valueB === 'string') {
          return sortDirection === 'asc' 
            ? valueA.localeCompare(valueB) 
            : valueB.localeCompare(valueA);
        }
        
        return sortDirection === 'asc' 
          ? (valueA < valueB ? -1 : valueA > valueB ? 1 : 0)
          : (valueB < valueA ? -1 : valueB > valueA ? 1 : 0);
      })
    : filteredItems;
  
  function toggleSort(column: string) {
    if (!sortable) return;
    
    if (sortColumn === column) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortColumn = column;
      sortDirection = 'asc';
    }
  }
</script>

<div class="table-widget">
  <div class="table-header">
    <h3>{title}</h3>
    
    {#if filterable}
      <div class="filter">
        <input 
          type="text" 
          placeholder="Filter..." 
          bind:value={filterText} 
        />
      </div>
    {/if}
  </div>
  
  {#if items.length === 0}
    <div class="no-data">No data available</div>
  {:else}
    <div class="table-container">
      <table>
        <thead>
          <tr>
            {#each processedColumns as column}
              <th 
                class:sortable
                class:sorted={sortColumn === column.key}
                class:asc={sortColumn === column.key && sortDirection === 'asc'}
                class:desc={sortColumn === column.key && sortDirection === 'desc'}
                on:click={() => toggleSort(column.key)}
              >
                {column.label}
                {#if sortable}
                  <span class="sort-icon">
                    {#if sortColumn === column.key}
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    {:else}
                      ⇵
                    {/if}
                  </span>
                {/if}
              </th>
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each sortedItems as item}
            <tr>
              {#each processedColumns as column}
                <td>{item[column.key] !== undefined ? item[column.key] : ''}</td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<style>
  .table-widget {
    background: var(--white);
    border-radius: 0.5rem;
    overflow: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid var(--gray-200);
  }
  
  h3 {
    margin: 0;
  }
  
  .filter input {
    padding: 0.5rem;
    border: 1px solid var(--gray-300);
    border-radius: 0.25rem;
    font-size: 0.875rem;
  }
  
  .no-data {
    padding: 2rem;
    text-align: center;
    color: var(--gray-400);
  }
  
  .table-container {
    overflow-x: auto;
    flex-grow: 1;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
  }
  
  th, td {
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid var(--gray-200);
  }
  
  th {
    background: var(--gray-50);
    font-weight: 600;
    position: sticky;
    top: 0;
  }
  
  th.sortable {
    cursor: pointer;
    user-select: none;
  }
  
  th.sortable:hover {
    background: var(--gray-100);
  }
  
  .sort-icon {
    display: inline-block;
    margin-left: 0.25rem;
    opacity: 0.5;
  }
  
  th.sorted .sort-icon {
    opacity: 1;
  }
  
  tr:hover {
    background-color: var(--gray-50);
  }
</style>