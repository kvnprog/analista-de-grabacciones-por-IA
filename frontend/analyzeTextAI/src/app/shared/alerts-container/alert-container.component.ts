import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { AlertService } from '../../services/alert.service'; // Ajusta la ruta
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-alert-container',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './alert-container.component.html',
    styleUrls: ['./alert-container.component.css']
})
export class AlertContainerComponent implements OnInit, OnDestroy{
    private timer: any;
    public alertStyles: Record<string, string> = {
        success: 'bg-[#f0fdf4] border-[#dcfce7] text-[#166534]',
        danger: 'bg-[#fef2f2] border-[#fee2e2] text-[#991b1b]',
        warning: 'bg-[#fffbeb] border-[#fef3c7] text-[#92400e]',
        info: 'bg-[#eff6ff] border-[#dbeafe] text-[#1e40af]'
    };

    public iconColors: Record<string, string> = {
        success: 'text-[#22c55e]',
        danger: 'text-[#ef4444]',
        warning: 'text-[#f59e0b]',
        info: 'text-[#3b82f6]'
    };

    constructor(public alertService: AlertService, private cdr: ChangeDetectorRef) {}

    ngOnInit() {
        this.timer = setInterval(() => {
        this.cdr.markForCheck(); 
        this.cdr.detectChanges();
        }, 500);
    }

    ngOnDestroy() {
        if (this.timer) clearInterval(this.timer);
    }
}