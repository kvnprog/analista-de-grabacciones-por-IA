import { Component, inject } from '@angular/core';
import { SidebarComponent } from '../../components/sidebar/sidebar';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../../services/auth.service';
import { TitleService } from '../../../../services/title-service.service';

interface UserProfile {
  name: string;
  last_name: string;
}

@Component({
  selector: 'app-layout',
  imports: [CommonModule, RouterOutlet, SidebarComponent],
  templateUrl: './layout.html',
  styleUrl: './layout.css',
})
export class LayoutComponent {
  sidebarCollapsed = false;
  full_name = "";
  id_user = 0;
  user_data: UserProfile = {
    name: '',
    last_name: ''
  };
  public titleService = inject(TitleService);

  constructor(
    private _auth: AuthService
  ){
    this.full_name = _auth.getFullName();
    this.id_user = _auth.getIdUser();
    this.user_data = _auth.getUserDetails() || { name: '', last_name: '' };
  }

  toggleSidebar() {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }
}
