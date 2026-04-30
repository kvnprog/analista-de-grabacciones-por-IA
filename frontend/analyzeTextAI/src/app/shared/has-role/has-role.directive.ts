import { Directive, Input, TemplateRef, ViewContainerRef } from '@angular/core';
import { AuthService } from '../../services/auth.service';

@Directive({ selector: '[appHasRole]', standalone: true })
export class HasRoleDirective {
  private hasView = false; // Control para no duplicar el elemento

  @Input() set appHasRole(roles: string[]) {
    const userRole = this.authService.getUserRole() || '';
    
    // Si el rol está incluido y no hemos creado la vista todavía
    if (roles.includes(userRole) && !this.hasView) {
      this.viewContainer.createEmbeddedView(this.templateRef);
      this.hasView = true;
    } 
    // Si el rol NO está incluido y la vista existe, la borramos
    else if (!roles.includes(userRole) && this.hasView) {
      this.viewContainer.clear();
      this.hasView = false;
    }
  }

  constructor(
    private templateRef: TemplateRef<any>, 
    private viewContainer: ViewContainerRef, 
    private authService: AuthService
  ) {}
}
