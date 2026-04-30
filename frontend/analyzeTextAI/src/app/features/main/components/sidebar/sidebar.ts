import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../../services/auth.service';
import { ApiService } from '../../../../services/api.service';
import { HasRoleDirective } from '../../../../shared/has-role/has-role.directive';

@Component({
  selector: 'app-sidebar',
  imports: [CommonModule, RouterModule, HasRoleDirective],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css',
})
export class SidebarComponent {
  @Input() isCollapsed = false;
  openMenu: string | null = null;

  constructor(
    private _api: ApiService,
    private _auth: AuthService,
  ){}

  toggleSubmenu(menu: string) {
    if (this.isCollapsed) return; // No abrir si está colapsado
    this.openMenu = this.openMenu === menu ? null : menu;
  }

  // Opcional: Cerrar submenús si se colapsa la sidebar desde el padre
  ngOnChanges() {
    if (this.isCollapsed) {
      this.openMenu = null;
    }
  }

  onLogout() {
    const url = `auth/logout`;
    this._api.put(url, {}).subscribe({
      next: async (res: any) => {
        console.log("Guardado", res)
        this._auth.clearSession()
        this._auth.clearStorage()
      },
      error: (err) => {
          console.error('Error en el request', err);
      }
    });
  }
}
