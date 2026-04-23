import { Routes } from '@angular/router';
import { Analyze } from './../../public/analyze/analyze';
import { LoginComponent } from './features/auth/pages/login/login';
import { LayoutComponent } from './features/main/pages/layout/layout';
import { authGuard, publicGuard } from './services/auth-guard.service';


export const routes: Routes = [
     { path: '', redirectTo: 'login', pathMatch: 'full' },
     { path: 'login', component: LoginComponent, canActivate: [publicGuard] },
     {
          path: 'layout',
          component: LayoutComponent,
          canActivate: [authGuard],
          children: [
               { 
                    path: 'home', 
                    loadComponent: () => import('./features/main/pages/home/home').then(m => m.HomeComponent) 
               },
               // 2. Hacemos que si llega a la raíz estando logueado, lo mande a home
               { path: '', redirectTo: 'home', pathMatch: 'full' },
               { 
                    path: 'analyze', 
                    loadComponent: () => import('../../public/analyze/analyze').then(m => m.Analyze) 
               },
          ]
     },
     { path: '**', redirectTo: 'login' }
];
