import { CommonModule } from "@angular/common";
import { Component, inject, OnInit } from "@angular/core";
import { TitleService } from "../../../../services/title-service.service";
import { ApiService } from "../../../../services/api.service";
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroArrowDownTraySolid, heroArrowPathSolid, heroPencilSolid, heroTrashSolid, heroUserPlusSolid } from '@ng-icons/heroicons/solid'
import { TooltipDirective } from "../../../../shared/tooltop-container/tooltip";
import { FormsModule, NgForm } from "@angular/forms";
import { AlertService } from "../../../../services/alert.service";
import { AlertPriService } from "../../../../services/alert-pri.service";
import * as XLSX from 'xlsx';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule, NgIcon, TooltipDirective, FormsModule],
  providers: [
    provideIcons({
      heroPencilSolid,
      heroArrowPathSolid,
      heroTrashSolid,
      heroUserPlusSolid,
      heroArrowDownTraySolid
    })
  ],
  templateUrl: './user-list.html',
  styleUrl: './user-list.css',
})
export class UserList implements OnInit {
  private titleService = inject(TitleService);
  private alertService = inject(AlertPriService);
  roles: string[] = [];
  campaigns: any[] = [];
  contactsDataSource: any[] = [];
  totalUsuarios = 0;
  page = 1;
  pageSize = 5;
  isLoading = false;
  usuarioSeleccionado: any = {
    data_user: { name: '', last_name: '', id_employed: '' },
    username: '',
    email: '',
    campaign_id: null,
    role: null
  };
  filteredUsers: any[] = [];
  filters = { search: '', role: '', campaign: '' };
  isOffcanvasOpen = false;
  formSubmitted = false;

  constructor(
    private _api: ApiService,
    private _alertService: AlertService
  ) {}

  ngOnInit() {
    this.titleService.setTitle('Administración usuarios');
    this.getUsers();
    this.getData();
  }

  getUsers() {
    const url = `users/`;
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

  getData() {
    const url = `users/get-data`;

    this._api.get(url).subscribe({
      next: (res: any) => {
        console.table(res);

        this.roles = res.roles; 
        this.campaigns = res.campaigns; 
      },
      error: (err) => {
        console.error('Error en el request para archivar campañas', err);
      }
    });
  }

  // Reemplaza el getter para que use tus datos actuales
  get usersPaginados() {
    const start = (this.page - 1) * this.pageSize;
    return this.filteredUsers.slice(start, start + this.pageSize);
  }

  get totalPages() {
    return Math.ceil(this.contactsDataSource.length / this.pageSize);
  }

  // Métodos de navegación
  nextPage() { if (this.page < this.totalPages) this.page++; }
  prevPage() { if (this.page > 1) this.page--; }


  openNewUser() {
    this.usuarioSeleccionado = {
      data_user: { name: '', last_name: '', id_employed: '' },
      username: '',
      email: '',
      campaign_id: null,
      role: null
    };
    console.log('Abriendo modal para nuevo usuario');
    this.isOffcanvasOpen = true;
  }

  // Método para abrir detalles/editar
  openDetails(contact: any) {
    console.log(contact)

    this.usuarioSeleccionado = { ...contact };
    console.log('Editando usuario:', contact.username);
    this.isOffcanvasOpen = true;
  }

  // Método para actualizar filtros
  updateFilter(event: any, type: string) {
    const value = event.target.value.toLowerCase();
    console.log(value)
  
    if (type === 'search') this.filters.search = value;
    if (type === 'role') this.filters.role = value;
    if (type === 'campaign') this.filters.campaign = value;

    this.page = 1; // Siempre resetear a la página 1
    this.applyFilters();
  }

  // Métodos de acciones
  async resetPass(id: number, username: string) {
    console.log('Reseteando password para:', username);
    const confirmed = await this.alertService.confirm({
      title: '¿Confirmar cambios?',
      message: `Esta acción actualizará la contraseña del usuario: ${username}. \n Esta acción no se puede deshacer.`,
      type: 'question',
      confirmText: 'Sí, actualizar',
      cancelText: 'No, revisar'
    });

    if (confirmed) {
      console.log('Procediendo a borrar en la API...');
      const url = `users/reset-password/${id}`;
      this._api.put(url, {}).subscribe({
        next: async (res: any) => {
          const confirmed = await this.alertService.confirm({
            title: '¡Actualizado!',
            message: `La contraseña del usuario ${username} se actualizo. <br> Nueva contraseña: <br><b style="font-size: 1.5em; color: #2c3e50;">${res.temp_password}</b>`,
            type: 'success',
            confirmText: 'Copiar y Cerrar'
          });

          if (confirmed) {
            navigator.clipboard.writeText(res.temp_password);
          }
        },
        error: (err) => {
            console.error('Error en el request para archivar campañas', err);
        }
      });
    }
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
      const url = `users/delete-user/${id}`;
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
      datosParaEnviar.data_user.id_employed = datosParaEnviar.data_user.id_employed || null;

      this._api.put(`users/${this.usuarioSeleccionado.id}`, datosParaEnviar).subscribe({
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
      this.usuarioSeleccionado.data_user.id_employed = this.usuarioSeleccionado.data_user.id_employed || null;

      this._api.post("users/", this.usuarioSeleccionado).subscribe({
        next: async (res: any) => {
          const confirmed = await this.alertService.confirm({
            title: 'Usuario Creado',
            message: `El usuario se creó correctamente. \n Contraseña: <br><b style="font-size: 1.5em; color: #2c3e50;">${res.temp_password}</b>`,
            type: 'success',
            confirmText: 'Copiar y Cerrar'
          });

          if (confirmed) {
            navigator.clipboard.writeText(res.temp_password);
          }

          this.closeOffcanvas();
          this.getUsers();
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

  applyFilters() {
    this.filteredUsers = this.contactsDataSource.filter(user => {
      // 1. Filtro de búsqueda (Nombre, Apellido o Username)
      const fullName = `${user.data_user?.name} ${user.data_user?.last_name}`.toLowerCase();
      const matchesSearch = !this.filters.search || 
                            fullName.includes(this.filters.search) || 
                            user.username?.toLowerCase().includes(this.filters.search);

      // 2. Filtro de Rol
      const matchesRole = !this.filters.role || user.role === this.filters.role;

      // 3. Filtro de Campaña
      const matchesCampaign = !this.filters.campaign || user.campaign?.name.toLowerCase() === this.filters.campaign;

      return matchesSearch && matchesRole && matchesCampaign;
    });

    this.totalUsuarios = this.filteredUsers.length;
  }

  closeOffcanvas() {
    this.isOffcanvasOpen = false;
    this.formSubmitted = false;
  }

  exportExcel() {
    console.log(this.filteredUsers)
    
    const datosLimpios = this.filteredUsers.map(user => {
      return {
        'ID': `#${user.id}`,
        'ID EMPLEADO': user.data_user?.id_employed || '',
        'NOMBRE': user.data_user?.name,
        'APELLIDOS': user.data_user?.last_name,
        'CORREO ELECTRONICO': user.email,
        'USUARIO': user.username,
        'CAMPAÑA': user.campaign?.name,
        'ROL': user.role.toUpperCase().replace('_', ' '),
        'STATUS': 1
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
