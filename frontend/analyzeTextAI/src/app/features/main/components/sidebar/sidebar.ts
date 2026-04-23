import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../../services/auth.service';

@Component({
  selector: 'app-sidebar',
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css',
})
export class SidebarComponent {
  @Input() isCollapsed = false;

  constructor(
    private _auth: AuthService,
  ){}

  onLogout() {
    this._auth.clearSession()
    this._auth.clearStorage()
  }
}
