<script lang="ts">
  import { PUBLIC_API_BASE_URL } from '$env/static/public';
  
  export let widget: any;
  export let data: any;
  export let ltmId: string;
  
  // Extract configuration
  const { buttons = [], layout = 'horizontal', title = null } = widget;
  
  async function performTransition(label: string, params = null) {
    try {
      const url = `${PUBLIC_API_BASE_URL}ltm/${ltmId}/transition`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          label,
          params,
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      // Could add feedback with a toast or other UI notification
    } catch (error) {
      console.error('Error performing transition:', error);
      // Handle error
    }
  }
</script>

<div class="buttons-widget {layout}">
  {#if title}
    <h3>{title}</h3>
  {/if}
  
  <div class="buttons-container">
    {#each buttons as button}
      <button 
        class={button.style || 'default'} 
        on:click={() => performTransition(button.transition, button.params || null)}
      >
        {button.label}
      </button>
    {/each}
  </div>
</div>

<style>
  .buttons-widget {
    padding: 1rem;
    border-radius: 0.5rem;
  }
  
  h3 {
    margin-top: 0;
    margin-bottom: 1rem;
  }
  
  .buttons-container {
    display: flex;
    gap: 0.5rem;
  }
  
  .horizontal .buttons-container {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .vertical .buttons-container {
    flex-direction: column;
  }
  
  .grid .buttons-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  button {
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    border: 1px solid var(--gray-300);
    background: var(--white);
    cursor: pointer;
    font-size: 0.875rem;
    transition: all 0.2s;
  }
  
  button:hover {
    background: var(--gray-100);
  }
  
  button.primary {
    background: var(--blue-500);
    color: white;
    border-color: var(--blue-600);
  }
  
  button.primary:hover {
    background: var(--blue-600);
  }
  
  button.success {
    background: var(--green-500);
    color: white;
    border-color: var(--green-600);
  }
  
  button.success:hover {
    background: var(--green-600);
  }
  
  button.danger {
    background: var(--red-500);
    color: white;
    border-color: var(--red-600);
  }
  
  button.danger:hover {
    background: var(--red-600);
  }
  
  button.warning {
    background: var(--yellow-500);
    color: white;
    border-color: var(--yellow-600);
  }
  
  button.warning:hover {
    background: var(--yellow-600);
  }
</style>