import { Injectable } from '@angular/core';

interface UserProfile {
  name: string;
  last_name: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  constructor() {}
  user_data: UserProfile = {
    name: '',
    last_name: ''
  };

  getUserDetails() {
    const userData = sessionStorage.getItem('user_id');
    if (userData) {
      try {
        const parsedData = JSON.parse(userData);
        return this.user_data = {
          name : parsedData.name,
          last_name: parsedData.last_name
        }; 
      } catch (e) {
        console.error("Error parseando el sessionStorage", e);
        return '';
      }
    }
    return '';
  }

  setDataInLocalStorage(variableName: string, data: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem(variableName, data);
    }
  }

  setToken(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
  }

  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }

  isLoggedIn(): boolean {
    if (typeof window === 'undefined') return false; // SSR: no hay sesión
    return !!this.getToken();
  }

  clearStorage() {
    if (typeof window !== 'undefined') {
      localStorage.clear();
      window.location.href = '/login';
    }
  }

  clearSession() {
    if (typeof window !== 'undefined') {
      sessionStorage.clear();
    }
  }

  getFullName() {
    const userData = sessionStorage.getItem('user_id');
    if (userData) {
      try {
        const parsedData = JSON.parse(userData);
        return `${parsedData.name} ${parsedData.last_name}`; 
      } catch (e) {
        console.error("Error parseando el sessionStorage", e);
        return '';
      }
    }
    return '';
  }

  getIdUser() {
    const userData = sessionStorage.getItem('user_id');
    if (userData) {
      try {
        const parsedData = JSON.parse(userData);
        return parsedData.user_id; 
      } catch (e) {
        console.error("Error parseando el sessionStorage", e);
        return '';
      }
    }
    return '';
  }
}
