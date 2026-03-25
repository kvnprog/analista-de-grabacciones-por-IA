import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { finalize } from 'rxjs/operators';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-analyze',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './analyze.html',
  styleUrls: ['./analyze.css']
})
export class Analyze {

  files: File[] = [];
  newWord: string = '';
  words: string[] = [];

  loading = false;    
  successMessage = ''; 

  constructor(private http: HttpClient,private cdr: ChangeDetectorRef) {}

  onFilesSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.files = Array.from(input.files);
    }
  }
  
  addWord() {
  const word = this.newWord.trim();
  if (word && !this.words.includes(word)) {
    this.words.push(word);
    this.newWord = '';
  }
}

  removeWord(index: number) {
  this.words.splice(index, 1);
}

clearWords() {
  this.words = [];
}

 submit() {
  if (!this.files.length || !this.words.length) {
    alert('Debes subir archivos y agregar palabras');
    return;
  }

  this.loading = true;
  this.successMessage = '';

  const formData = new FormData();
  this.files.forEach(file => formData.append('files', file));
  formData.append('words', this.words.join(','));

  this.http.post(
    'http://172.18.232.195:9100/analyze-text',
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
