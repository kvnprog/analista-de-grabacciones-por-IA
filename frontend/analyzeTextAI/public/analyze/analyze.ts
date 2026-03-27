import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { NgSelectModule } from '@ng-select/ng-select';
import { ChangeDetectorRef } from '@angular/core';

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
  loading = false;    
  successMessage = ''; 
  constructor(private http: HttpClient,private cdr: ChangeDetectorRef) {}
  isOver = false;
  audioList: AudioFile[] = [];
  selectedTags: string[] = [];
  files: File[] = [];

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
        alert(`El archivo ${file.name} no es un formato válido (Solo MP3 o WAV)`);
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

    if (!this.audioList.length || !this.selectedTags.length) {
      alert('Debes subir archivos y agregar palabras');
      return;
    }

    this.loading = true;
    this.successMessage = '';

    const formData = new FormData();
    this.files.forEach(file => formData.append('files', file));
    formData.append('words', this.selectedTags.join(','));

    this.http.post(
      'http://localhost:9100/analyze-text',
      formData,
      { responseType: 'blob' }
    ).subscribe({
      next: (blob) => {
        this.loading = false;
        this.successMessage = '✅ Proceso terminado correctamente';

        this.cdr.detectChanges(); // 🔥 fuerza render

        this.downloadExcel(blob);
      },
      error: () => {
        this.loading = false;
        alert('❌ Ocurrió un error durante el análisis');
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
}
