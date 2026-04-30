import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

export interface AlertOptions {
    title: string;
    message: string;
    type: 'success' | 'error' | 'warning' | 'question';
    confirmText?: string;
    cancelText?: string;
}

@Injectable({ providedIn: 'root' })
export class AlertPriService {
    private alertSubject = new Subject<{ options: AlertOptions, resolve: (val: boolean) => void }>();
    alertState$ = this.alertSubject.asObservable();

    // Esta función devuelve una Promesa, permitiendo usar await
    confirm(options: AlertOptions): Promise<boolean> {
        return new Promise((resolve) => {
            this.alertSubject.next({ options, resolve });
        });
    }
}