import { inject, Injectable } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

// auth.guard.ts (Para proteger el Layout/Dashboard)
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn()) {
    return true;
  } else {
    return router.parseUrl('/login');
  }
};

// public.guard.ts (Para el Login)
export const publicGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn()) {
    return router.parseUrl('/layout/home'); // Si ya está logueado, mandarlo al inicio
  }
  return true;
};

export const roleGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const userData = authService.getUserData(); // El método que creamos antes
  console.log("---------", userData)
  const requiredRoles = route.data['roles'] as Array<string>;

  // 1. Si no hay datos de usuario, al login
  if (!userData) {
    return router.parseUrl('/login');
  }

  // 2. Si la ruta requiere roles y el rol del usuario no está en la lista
  if (requiredRoles && !requiredRoles.includes(userData.user_role)) {
    console.warn('Acceso denegado: No tienes el rol necesario');
    return router.parseUrl('/layout/home'); // Redirigir a una zona segura
  }

  return true; // Acceso concedido
};