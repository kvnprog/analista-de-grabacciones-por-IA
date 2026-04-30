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
    const userData = localStorage.getItem('user_data');
    console.log(userData)
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

  setData(data: object) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('user_data', JSON.stringify(data));
    }
  }

  getUserData() {
    if (typeof window !== 'undefined') {
      const data = localStorage.getItem('user_data');
      return data ? JSON.parse(data) : null;
    }
    return null;
  }

  getUserRole(): string | null {
    const user = this.getUserData();
    return user ? user.user_role : null;
  }

  isLoggedIn(): boolean {
    if (typeof window === 'undefined') return false;
    // Si existe el objeto user_data, asumimos que está logueado
    return !!this.getUserData();
  }

  clearStorage() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('user_data');
      window.location.href = '/login';
    }
  }

  clearSession() {
    if (typeof window !== 'undefined') {
      sessionStorage.clear();
    }
  }

  getFullName() {
    const userData = localStorage.getItem('user_data');
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
    const userData = localStorage.getItem('user_data');
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
