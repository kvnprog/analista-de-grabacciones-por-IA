import { Injectable, NgZone } from '@angular/core';

export interface Alert {
    icon: 'check' | 'error' | 'warning' | 'info';
    tipeAlert: 'success' | 'danger' | 'warning' | 'info';
    title: string;
    text: string;
    id?: number;
}

@Injectable({
    providedIn: 'root'
})
export class AlertService {
    public alerts: Alert[] = [];
    private counter = 0;

    constructor(private zone: NgZone) {}

    show(alert: Alert, duration: number = 5000) {
        const id = this.counter++;
        this.alerts.push({ ...alert, id });

        setTimeout(() => {
            this.zone.run(() => {
                this.remove(id);
            });
        }, duration);
    }

    success(title: string, text: string) {
        this.show({ tipeAlert: 'success', icon: 'check', title, text });
    }

    error(title: string, text: string) {
        this.show({ tipeAlert: 'danger', icon: 'error', title, text });
    }

    remove(id: number) {
        this.alerts = [...this.alerts.filter(a => a.id !== id)];
    }
}