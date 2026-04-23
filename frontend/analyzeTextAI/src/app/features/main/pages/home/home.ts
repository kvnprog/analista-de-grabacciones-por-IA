import { Component, inject, OnInit } from '@angular/core';
import { TitleService } from '../../../../services/title-service.service';

@Component({
  selector: 'app-home',
  imports: [],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class HomeComponent implements OnInit {
  private titleService = inject(TitleService);

  ngOnInit() {
    this.titleService.setTitle('Inicio');
  }
}
