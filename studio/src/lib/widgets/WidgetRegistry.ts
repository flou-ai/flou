import type { ComponentType } from 'svelte';

// Define widget component interface
export interface WidgetComponent {
  // Component props type
}

// Widget registry to manage component registration
export class WidgetRegistry {
  private static widgets = new Map<string, ComponentType>();
  
  // Register a widget component
  static register(type: string, component: ComponentType): void {
    this.widgets.set(type, component);
  }
  
  // Get a widget component by type
  static getComponent(type: string): ComponentType | undefined {
    return this.widgets.get(type);
  }
  
  // Check if a widget type is registered
  static hasWidget(type: string): boolean {
    return this.widgets.has(type);
  }
  
  // Get all registered widget types
  static getWidgetTypes(): string[] {
    return Array.from(this.widgets.keys());
  }
}