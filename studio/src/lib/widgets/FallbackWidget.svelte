<script lang="ts">
  import { JsonView } from '@zerodevx/svelte-json-view';
  
  export let widget: any;
  export let data: any;
  export let ltmId: string;
</script>

<div class="fallback-widget">
  <h3>Unknown Widget: {widget.type}</h3>
  <div class="widget-data">
    <h4>Widget Configuration:</h4>
    <JsonView json={widget} />
    
    <h4>Widget Data:</h4>
    <JsonView json={data} />
  </div>
</div>

<style>
  .fallback-widget {
    padding: 1rem;
    border: 1px dashed var(--gray-400);
    border-radius: 0.5rem;
  }
  
  .widget-data {
    margin-top: 1rem;
  }
  
  h3 {
    color: var(--red-500);
    margin: 0;
  }
  
  h4 {
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
  }
</style>