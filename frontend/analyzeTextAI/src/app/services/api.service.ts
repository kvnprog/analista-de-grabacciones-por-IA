import { HttpClient, HttpHeaders, HttpParams, HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environment';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  constructor(private httpClient: HttpClient) {}

  // GET con parámetros opcionales
  get(url: string, params?: HttpParams): Observable<any> {
    return this.httpClient.get(`${environment.apiUrl}/${url}`, { params });
  }

  // POST genérico
  post(url: string, payload: any, options?: any): Observable<any> {
    return this.httpClient.post(`${environment.apiUrl}/${url}`, payload, options);
  }

  // PUT genérico
  put(url: string, payload: any, options?: any): Observable<any> {
    return this.httpClient.put(`${environment.apiUrl}/${url}`, payload, options);
  }

  // DELETE genérico
  delete(url: string, options?: any): Observable<any> {
    return this.httpClient.delete(`${environment.apiUrl}/${url}`, options);
  }

  // POST con FormData
  postFormData(url: string, formData: FormData): Observable<any> {
    return this.httpClient.post(`${environment.apiUrl}/${url}`, formData);
  }

  // POST con x-www-form-urlencoded
  postUrlEncoded(url: string, payload: any): Observable<any> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });
    return this.httpClient.post(`${environment.apiUrl}/${url}`, payload, { headers });
  }

  // Descargar archivo Excel
  getExcelFile(url: string): Observable<HttpResponse<Blob>> {
    return this.httpClient.get(`${environment.apiUrl}/${url}`, {
      observe: 'response',
      responseType: 'blob'
    });
  }

  getExcelFileData(url: string, params: HttpParams): Observable<HttpResponse<Blob>> {
  return this.httpClient.get(`${environment.apiUrl}/${url}`, {
    params,
    observe: 'response',
    responseType: 'blob'
  });
}

  // Descargar ZIP de audios
  getAudioZip(campaignId: number): Observable<HttpResponse<Blob>> {
    return this.httpClient.get(`${environment.apiUrl}/campaign/${campaignId}/download-audios`, {
      observe: 'response',
      responseType: 'blob'
    });
  }
}
