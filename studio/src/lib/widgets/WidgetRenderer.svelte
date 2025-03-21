<script lang="ts">
  import { WidgetRegistry } from './WidgetRegistry';
  import FallbackWidget from './FallbackWidget.svelte';
  
  export let widget: any;
  export let data: any;
  export let ltmId: string;
  
  // Get the component for this widget type
  $: Component = WidgetRegistry.getComponent(widget.type) || FallbackWidget;
</script>

<svelte:component this={Component} {widget} {data} {ltmId} />