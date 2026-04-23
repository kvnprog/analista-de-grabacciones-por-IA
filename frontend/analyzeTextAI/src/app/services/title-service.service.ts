import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class TitleService {
  public moduleTitle = signal<string>('Inicio');

  setTitle(newTitle: string) {
    this.moduleTitle.set(newTitle);
  }
}
