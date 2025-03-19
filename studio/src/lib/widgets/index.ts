import ChatWidget from './ChatWidget.svelte';
import TableWidget from './TableWidget.svelte';
import ButtonsWidget from './ButtonsWidget.svelte';
import SubLTMWidget from './SubLTMWidget.svelte';
import KeyValueWidget from './KeyValueWidget.svelte';
import ListWidget from './ListWidget.svelte';
import { WidgetRegistry } from './WidgetRegistry';

// Register built-in widgets
WidgetRegistry.register('chat', ChatWidget);
WidgetRegistry.register('table', TableWidget);
WidgetRegistry.register('buttons', ButtonsWidget);
WidgetRegistry.register('subLTM', SubLTMWidget);
WidgetRegistry.register('keyValue', KeyValueWidget);
WidgetRegistry.register('list', ListWidget);

export { WidgetRegistry };