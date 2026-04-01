import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { NgSelectModule } from '@ng-select/ng-select';
import { ChangeDetectorRef } from '@angular/core';
import { finalize } from 'rxjs/operators';
import { AlertService } from '../../src/app/services/alert.service';

interface AudioFile {
  file: File;
  url: string;
  name: string;
  size: string;
  format: string;
}

@Component({
  selector: 'app-analyze',
  standalone: true,
  imports: [CommonModule, FormsModule, NgSelectModule],
  templateUrl: './analyze.html',
  styleUrls: ['./analyze.css']
})
export class Analyze {
  constructor(
    private http: HttpClient,
    private cdr: ChangeDetectorRef,
    private alertService: AlertService
  ) {}
  loading = false;    
  successMessage = ''; 
  isOver = false;
  audioList: AudioFile[] = [];
  selectedTags: string[] = [];
  files: File[] = [];
  opcionA: boolean = false;
  opcionB: boolean = false;
  textoBusqueda: string = '';

  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isOver = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isOver = false;
    if (event.dataTransfer?.files) {
      this.processFiles(event.dataTransfer.files);
    }
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.processFiles(input.files);
    }
  }

  private processFiles(files: FileList) {
    const allowedExtensions = ['mp3', 'wav'];
    
    Array.from(files).forEach(file => {
      const extension = file.name.split('.').pop()?.toLowerCase();
      
      if (extension && allowedExtensions.includes(extension)) {
        this.audioList.push({
          file: file,
          name: file.name,
          format: extension.toUpperCase(),
          size: (file.size / (1024 * 1024)).toFixed(2) + ' MB',
          url: URL.createObjectURL(file) // Creamos el preview
        });

        this.files.push(file);
      } else {
        this.alertService.error(
          '¡Error en el archivo!', 
          `El archivo ${file.name} no es un formato válido (Solo MP3 o WAV)`
        );
      }
    });
  }

  removeFile(index: number) {
    URL.revokeObjectURL(this.audioList[index].url);
    this.audioList.splice(index, 1);
    this.files.splice(index, 1);
  }

  submit() {
    console.log('Tags seleccionados:', this.selectedTags);
    if (!this.validData())
      return;

    this.loading = true;
    this.successMessage = '';

    const formData = new FormData();
    this.files.forEach(file => formData.append('files', file));
    formData.append('words', this.selectedTags.join(',') || ""); // Asegura que no sea null
    formData.append('textSearch', this.textoBusqueda || "");

    this.http.post(
      'http://localhost:9100/analyze-text',
      formData,
      { responseType: 'blob' }
    ).pipe(
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (blob) => {        
        this.successMessage = '✅ Proceso terminado correctamente';
        this.alertService.success(
          '¡Correcto!', 
          'Proceso terminado correctamente'
        );

        this.downloadExcel(blob);
        this.cleanForm();
      },
      error: (err) => {
        console.error('Error en la petición', err);
        this.alertService.error(
          '¡Error fatal!', 
          'Error en la petición o en el procesamiento'
        );
      }
    });
  }

  private downloadExcel(blob: Blob) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'analisis_texto.xlsx';
    a.click();
    window.URL.revokeObjectURL(url);
  }

  private validData() {
    let oValidacion: boolean = true;

    if (this.opcionA == false && this.opcionB == false){
      this.alertService.error(
        '¡Error en formulario!', 
        'Debes seleccionar alguna forma de busqueda'
      );
      oValidacion = false;  
    } else {
      if (this.opcionA == true) {
        if (!this.audioList.length || !this.selectedTags.length) {
          this.alertService.error(
            '¡Error en formulario!', 
            'Debes subir archivos y agregar palabras'
          );
          oValidacion = false;
        }
      }

      if (this.opcionB == true) {
        if (!this.audioList.length || !this.textoBusqueda.length) {
          this.alertService.error(
            '¡Error en formulario!', 
            'Debes subir archivos y agregar alguna busqueda'
          );
          oValidacion = false;
        }
      }
    }

    return oValidacion;
  }

  onCheckChange(tipo: 'A' | 'B') {
    if (tipo === 'A') {
      this.selectedTags = [];
    }
    
    if (tipo === 'B') {
      this.textoBusqueda = "";
    }
  }

  private cleanForm() {
    this.opcionA = false;
    this.opcionB = false;
    this.selectedTags = [];
    this.textoBusqueda = "";
    this.audioList = [];
    this.files = [];
  }
}
