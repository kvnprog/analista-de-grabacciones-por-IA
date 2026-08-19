import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { NgSelectModule } from '@ng-select/ng-select';
import { ChangeDetectorRef } from '@angular/core';
import { finalize } from 'rxjs/operators';
import { AlertService } from '../../src/app/services/alert.service';
import { TitleService } from '../../src/app/services/title-service.service';
import { environment } from '../../src/environment';

type TipoEntrada = 'audio' | 'texto';

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
export class Analyze implements OnInit {
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
  opcionC: boolean = false; // Detectar emociones
  opcionD: boolean = false; // Preguntas desde Excel
  textoBusqueda: string = '';
  questionsExcelFile: File | null = null; // Nuevo: archivo Excel con preguntas
  private titleService = inject(TitleService);

  tipoEntrada: TipoEntrada = 'audio';

  private readonly extensionesPorTipo: Record<TipoEntrada, string[]> = {
    audio: ['mp3', 'wav'],
    texto: ['txt']
  };

  private readonly acceptPorTipo: Record<TipoEntrada, string> = {
    audio: '.mp3,.wav,audio/mpeg,audio/wav,audio/x-wav',
    texto: '.txt,text/plain'
  };

  get acceptString(): string {
    return this.acceptPorTipo[this.tipoEntrada];
  }

  get extensionesPermitidas(): string[] {
    return this.extensionesPorTipo[this.tipoEntrada];
  }

  get hintTexto(): string {
    return this.tipoEntrada === 'audio' ? 'MP3, WAV' : 'TXT';
  }

  get tituloUpload(): string {
    return this.tipoEntrada === 'audio' ? 'Subir grabaciones' : 'Subir transcripciones';
  }

  ngOnInit() {
    this.titleService.setTitle('Sistema de búsqueda por grabaciones mediante IA');
  }

  setTipoEntrada(tipo: TipoEntrada) {
    if (this.tipoEntrada === tipo) return;

    this.tipoEntrada = tipo;
    this.limpiarArchivos();

    if (tipo === 'texto') {
      this.opcionC = false;
    }
  }

  private limpiarArchivos() {
    this.audioList.forEach(item => URL.revokeObjectURL(item.url));
    this.audioList = [];
    this.files = [];
  }

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
    input.value = '';
  }

  private processFiles(files: FileList) {
    const allowedExtensions = this.extensionesPermitidas;

    Array.from(files).forEach(file => {
      const extension = file.name.split('.').pop()?.toLowerCase();

      if (extension && allowedExtensions.includes(extension)) {
        this.audioList.push({
          file: file,
          name: file.name,
          format: extension.toUpperCase(),
          size: (file.size / (1024 * 1024)).toFixed(2) + ' MB',
          url: URL.createObjectURL(file)
        });

        this.files.push(file);
      } else {
        const formatosValidos = this.tipoEntrada === 'audio' ? 'MP3 o WAV' : 'TXT';
        this.alertService.error(
          '¡Error en el archivo!',
          `El archivo ${file.name} no es un formato válido (Solo ${formatosValidos})`
        );
      }
    });
  }

  removeFile(index: number) {
    URL.revokeObjectURL(this.audioList[index].url);
    this.audioList.splice(index, 1);
    this.files.splice(index, 1);
  }

  // --- Nuevo: manejo del Excel de preguntas ---
  onQuestionsExcelSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      const ext = file.name.split('.').pop()?.toLowerCase();

      if (ext === 'xlsx' || ext === 'xls') {
        this.questionsExcelFile = file;
      } else {
        this.alertService.error(
          '¡Error en el archivo!',
          'Debes subir un archivo Excel válido (.xlsx o .xls)'
        );
      }
    }
    input.value = '';
  }

  removeQuestionsExcel() {
    this.questionsExcelFile = null;
  }

  submit() {
    if (!this.validData())
      return;

    this.loading = true;
    this.successMessage = '';

    const formData = new FormData();
    this.files.forEach(file => formData.append('files', file));
    formData.append('words', this.selectedTags.join(',') || "");
    formData.append('textSearch', this.textoBusqueda || "");
    formData.append('tipoEntrada', this.tipoEntrada);
    formData.append('detectarEmociones', this.opcionC ? 'true' : 'false');

    if (this.opcionD && this.questionsExcelFile) {
      formData.append('questionsFile', this.questionsExcelFile);
    }

    this.http.post(
      environment.apiUrl + "/analyze-text",
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

    if (this.opcionA == false && this.opcionB == false && this.opcionC == false && this.opcionD == false) {
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

      if (this.opcionC == true) {
        if (!this.audioList.length) {
          this.alertService.error(
            '¡Error en formulario!',
            'Debes subir archivos de audio para detectar emociones'
          );
          oValidacion = false;
        }
        if (this.tipoEntrada !== 'audio') {
          this.alertService.error(
            '¡Error en formulario!',
            'La detección de emociones solo aplica para archivos de audio'
          );
          oValidacion = false;
        }
      }

      if (this.opcionD == true) {
        if (!this.audioList.length) {
          this.alertService.error(
            '¡Error en formulario!',
            'Debes subir archivos para responder las preguntas del Excel'
          );
          oValidacion = false;
        }
        if (!this.questionsExcelFile) {
          this.alertService.error(
            '¡Error en formulario!',
            'Debes subir el Excel con las preguntas'
          );
          oValidacion = false;
        }
      }
    }

    return oValidacion;
  }

  onCheckChange(tipo: 'A' | 'B' | 'C' | 'D') {
    if (tipo === 'A') {
      this.selectedTags = [];
    }

    if (tipo === 'B') {
      this.textoBusqueda = "";
    }

    if (tipo === 'D' && !this.opcionD) {
      this.questionsExcelFile = null;
    }
  }

  private cleanForm() {
    this.opcionA = false;
    this.opcionB = false;
    this.opcionC = false;
    this.opcionD = false;
    this.selectedTags = [];
    this.textoBusqueda = "";
    this.questionsExcelFile = null;
    this.limpiarArchivos();
  }
}