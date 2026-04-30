import { Component, inject, OnInit } from '@angular/core';
import { TitleService } from '../../../../services/title-service.service';
import { CommonModule } from '@angular/common';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroArrowDownTraySolid, heroArrowPathSolid, heroPencilSolid, heroTrashSolid, heroUserPlusSolid } from '@ng-icons/heroicons/solid'
import { FormsModule, NgForm } from '@angular/forms';
import { ApiService } from '../../../../services/api.service';
import { AlertService } from '../../../../services/alert.service';
import { AlertPriService } from '../../../../services/alert-pri.service';
import { TooltipDirective } from '../../../../shared/tooltop-container/tooltip';
import * as XLSX from 'xlsx';

@Component({
  selector: 'app-user-concentration',
  imports: [
    CommonModule, NgIcon, FormsModule, TooltipDirective
  ],
  providers: [
    provideIcons({
      heroPencilSolid,
      heroArrowPathSolid,
      heroTrashSolid,
      heroUserPlusSolid,
      heroArrowDownTraySolid
    })
  ],
  templateUrl: './user-concentration.html',
  styleUrl: './user-concentration.css',
})
export class UserConcentration implements OnInit {
  private titleService = inject(TitleService);
  private alertService = inject(AlertPriService);
  usuarioSeleccionado: any = {
    id_employed: '',
    username: '',
    password: '',
    name: '',
    client: null,
    plataform: null,
    role: null
  };
  isOffcanvasOpen = false;
  formSubmitted = false;
  isLoading = false;
  contactsDataSource: any[] = [];
  totalUsuarios = 0;
  page = 1;
  pageSize = 5;
  filteredUsers: any[] = [];
  filters = { search: '' };

  constructor(
    private _api: ApiService,
    private _alertService: AlertService
  ) {}

  ngOnInit() {
    this.titleService.setTitle('Concentrado de usuarios');
    this.getUsers();
  }

  getUsers() {
    const url = `users-ctn/`;
    this.isLoading = true;

    this._api.get(url).subscribe({
      next: (res: any) => {
        console.table(res)
        this.contactsDataSource = res
        this.totalUsuarios = res.length;
        this.applyFilters();

        console.table(this.contactsDataSource)
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error en el request para archivar campañas', err);
      }
    });
  }

  saveUser(form: NgForm) {
    this.formSubmitted = true;
    console.log('Guardando datos de:', this.usuarioSeleccionado);

    if (form.invalid) {
      console.log('Formulario inválido, revisa los campos en rojo');
      return; // Detenemos el guardado si hay errores
    }

    if (this.usuarioSeleccionado.id) {
      const { campaign, ...datosParaEnviar } = this.usuarioSeleccionado;
      console.log(datosParaEnviar)
      console.log("------------------------------------")
      datosParaEnviar.id_employed = datosParaEnviar.id_employed || null;

      this._api.put(`users-ctn/${this.usuarioSeleccionado.id}`, datosParaEnviar).subscribe({
        next: (res: any) => {
          console.table(res);
          this._alertService.success(
            'Actualización correcta', 
            `Se actualizo la información del usuario: ${res.user.username}`
          );
          this.getUsers();
          this.closeOffcanvas();
        },
        error: (err) => {
          console.error('Error en el request', err);
          this._alertService.error(
            'Error en la app', 
            `Error: ${err.error.detail}`
          );
        }
      });
    } else {
      this.usuarioSeleccionado.id_employed = this.usuarioSeleccionado.id_employed || null;
      console.log(this.usuarioSeleccionado)

      this._api.post("users-ctn/", this.usuarioSeleccionado).subscribe({
        next: async (res: any) => {
          const confirmed = await this.alertService.confirm({
            title: 'Usuario Creado',
            message: `El usuario se creó correctamente con el id: ${res.user.id}`,
            type: 'success',
            confirmText: 'Copiar y Cerrar'
          });

          if (confirmed) {
            navigator.clipboard.writeText(res.temp_password);
          }

          this.closeOffcanvas();
          //this.getUsers();
        },
        error: (err) => {
          console.error('Error en el request', err);
          this._alertService.error(
            'Error en la app', 
            `Error: ${err.error.detail}`
          );
        }
      });
    }
  }

  openNewUser() {
    this.usuarioSeleccionado = {
      id_employed: '',
      username: '',
      password: '',
      name: '',
      client: null,
      plataform: null,
      role: null
    };
    console.log('Abriendo modal para nuevo usuario');
    this.isOffcanvasOpen = true;
  }

  openDetails(contact: any) {
    this.usuarioSeleccionado = { ...contact };
    console.log('Editando usuario:', contact.username);
    this.isOffcanvasOpen = true;
  }

  async deleteUser(id: number, username: string) {
    console.log('Eliminando usuario:', username);
    const confirmed = await this.alertService.confirm({
      title: '¿Confirmar eliminación?',
      message: `Esta acción eliminara al usuario: ${username}`,
      type: 'question',
      confirmText: 'Sí, eliminar',
      cancelText: 'No, revisar'
    });

    if (confirmed) {
      const url = `users-ctn/delete-user/${id}`;
      this._api.delete(url).subscribe({
        next: (res: any) => {
          this._alertService.success(
            'Eliminación correcta', 
            `Se elimino el usuario: ${username}`
          );

          this.getUsers();
        },
        error: (err) => {
          console.error('Error en el request para archivar campañas', err);
        }
      });
    }
  }

  updateFilter(event: any, type: string) {
    const value = event.target.value.toLowerCase();
    console.log(value)
  
    if (type === 'search') this.filters.search = value;

    this.page = 1; // Siempre resetear a la página 1
    this.applyFilters();
  }

  closeOffcanvas() {
    this.isOffcanvasOpen = false;
    this.formSubmitted = false;
  }

  applyFilters() {
    this.filteredUsers = this.contactsDataSource.filter(user => {
      // 1. Filtro de búsqueda (Nombre, Apellido o Username)
      const fullName = `${user.data_user?.name} ${user.data_user?.last_name}`.toLowerCase();
      const matchesSearch = !this.filters.search || 
                            fullName.includes(this.filters.search) || 
                            user.username?.toLowerCase().includes(this.filters.search);

      return matchesSearch;
    });

    this.totalUsuarios = this.filteredUsers.length;
  }


  get usersPaginados() {
    const start = (this.page - 1) * this.pageSize;
    return this.filteredUsers.slice(start, start + this.pageSize);
  }

  get totalPages() {
    return Math.ceil(this.contactsDataSource.length / this.pageSize);
  }

  nextPage() { if (this.page < this.totalPages) this.page++; }
  prevPage() { if (this.page > 1) this.page--; }

  exportExcel() {
    console.log(this.filteredUsers)
    
    const datosLimpios = this.filteredUsers.map(user => {
      return {
        'Id': `#${user.id}`,
        'Fecha': new Date(user.created_at).toLocaleDateString('es-MX'),
        'Empleado': user.id_employed == null ? '' : user.id_employed,
        'Nombre': user.name,
        'Cliente': user.client,
        'Plataforma': user.plataform,
        'Usuario': user.username,
        'Password': user.password,
        'Estado': user.status == 1 ? 'Activo' : 'Inactivo',
        'Rol': user.role.toUpperCase().replace('_', ' ')
      };
    });

    const worksheet: XLSX.WorkSheet = XLSX.utils.json_to_sheet(datosLimpios);

    const objectMaxLength: number[] = [];
    const keys = Object.keys(datosLimpios[0]);

    if (datosLimpios.length > 0) {
      const objectMaxLength: any[] = [];
      
      // Obtenemos las llaves del primer objeto
      const keys = Object.keys(datosLimpios[0]);

      keys.forEach((key, i) => {
        // 1. Calculamos el largo del nombre de la columna (el encabezado)
        let maxColumnLength = key.length;

        // 2. Recorremos las filas para encontrar el dato más largo
        datosLimpios.forEach(row => {
          // SOLUCIÓN AL ERROR TS(7053):
          // Forzamos a que 'row' se trate como un diccionario indexable por string
          const cellValue = (row as { [key: string]: any })[key];
          
          const length = cellValue ? cellValue.toString().length : 0;
          if (length > maxColumnLength) {
            maxColumnLength = length;
          }
        });

        objectMaxLength[i] = { wch: maxColumnLength + 2 };
      });

      worksheet['!cols'] = objectMaxLength;
    }

    // 2. Crear un libro de trabajo (workbook)
    const workbook: XLSX.WorkBook = { 
      Sheets: { 'Datos': worksheet }, 
      SheetNames: ['Datos'] 
    };

    // 3. Generar el archivo y descargarlo
    XLSX.writeFile(workbook, `Usuarios_${new Date().getTime()}.xlsx`);
  }
}
