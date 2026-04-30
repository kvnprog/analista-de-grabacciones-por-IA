import { Directive, ElementRef, HostListener, Input, Renderer2 } from '@angular/core';

@Directive({
  selector: '[appTooltip]',
  standalone: true
})
export class TooltipDirective {
  @Input('appTooltip') tooltipText: string = '';
  @Input() tooltipColor: string = 'bg-gray-800';
  private tooltipElement: HTMLElement | null = null;

  constructor(private el: ElementRef, private renderer: Renderer2) {}

  @HostListener('mouseenter') onMouseEnter() {
    if (!this.tooltipText) return;
    this.show();
  }

  @HostListener('mouseleave') onMouseLeave() {
    this.hide();
  }

  private show() {
    // 1. Crear el elemento span
    this.tooltipElement = this.renderer.createElement('span');
    this.renderer.appendChild(
      this.tooltipElement,
      this.renderer.createText(this.tooltipText)
    );

    // 2. Aplicar clases de Tailwind para diseño profesional
    const classes = [
      'fixed', 'z-50', 'px-2', 'py-1', 'text-xs', 'text-white', 
      'rounded', 'shadow-lg', 'transition-opacity', 'pointer-events-none'
    ];
    classes.forEach(cls => this.renderer.addClass(this.tooltipElement, cls));
    this.renderer.addClass(this.tooltipElement, this.tooltipColor);

    // 3. Posicionamiento dinámico
    this.renderer.appendChild(document.body, this.tooltipElement);
    const hostPos = this.el.nativeElement.getBoundingClientRect();
    
    const top = hostPos.top - 30; // Un poco arriba del elemento
    const left = hostPos.left + (hostPos.width / 2);

    this.renderer.setStyle(this.tooltipElement, 'top', `${top}px`);
    this.renderer.setStyle(this.tooltipElement, 'left', `${left}px`);
    this.renderer.setStyle(this.tooltipElement, 'transform', 'translateX(-50%)');
  }

  private hide() {
    if (this.tooltipElement) {
      this.renderer.removeChild(document.body, this.tooltipElement);
      this.tooltipElement = null;
    }
  }
}