import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { APP_VERSION } from '../version';
import { AlertContainerComponent } from './shared/alerts-container/alert-container.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, AlertContainerComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('analyzeTextAI');
  version = APP_VERSION;
}
