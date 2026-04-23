import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { ApiService } from '../../../../services/api.service';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { AuthService } from '../../../../services/auth.service';
import { AlertService } from '../../../../services/alert.service';

@Component({
  selector: 'app-login',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class LoginComponent implements OnInit {
  form: FormGroup;
  private isBrowser: boolean;
  rememberMe: boolean = false;

  constructor(
    private _api: ApiService,
    private _router: Router,
    private _auth: AuthService,
    private _fb: FormBuilder,
    private _alertService: AlertService,
    @Inject(PLATFORM_ID) private platformId: Object
  ){
    this.isBrowser = isPlatformBrowser(this.platformId);

    this.form = this._fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required],
      remember: [false]
    });
  }

  ngOnInit() {
    if (this.isBrowser) {
      const savedUser = localStorage.getItem('remembered_user');
      const savedPassword = localStorage.getItem('remembered_password');
      if (savedUser) {
        this.form.patchValue({
          username: savedUser,
          password: savedPassword,
          remember: true
        });
      }
    }
  }

  onLogin() {
    const { username, password, remember } = this.form.value;

    this._api.post('auth/login', { username, password }).subscribe({
      next: (res: any) => {
        if (res.access_token) {
          this._auth.setToken(res.access_token);
          sessionStorage.setItem('user_id', JSON.stringify(res));

          if (this.isBrowser) {
            if (remember) {
              localStorage.setItem('remembered_user', username);
              localStorage.setItem('remembered_password', password);
            } else {
              localStorage.removeItem('remembered_user');
              localStorage.removeItem('remembered_password');
            }
          }

          this._alertService.success(
            'Iniciaste sesión', 
            `Bienvenid@. Tu espacio está listo.`
          );

          this._router.navigate(['/layout']);
        }
      },
      error: (err) => {
        console.log(err)
        this._alertService.error(
          '¡Error fatal!', 
          `Usuario o contraseña incorrectos: ${err.status}`
        );
      }
    });
  }
}
