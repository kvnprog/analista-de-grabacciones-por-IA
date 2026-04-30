import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AlertPriService, AlertOptions } from '../../services/alert-pri.service';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroQuestionMarkCircleSolid, heroXCircleSolid, heroCheckCircleSolid, heroExclamationTriangleSolid } from '@ng-icons/heroicons/solid'

@Component({
    selector: 'app-pri-alert-container',
    standalone: true,
    imports: [CommonModule, NgIcon],
    providers: [
        provideIcons({
            heroQuestionMarkCircleSolid,
            heroXCircleSolid,
            heroCheckCircleSolid,
            heroExclamationTriangleSolid
        })
    ],
    template: `
        <div *ngIf="isOpen" class="fixed inset-0 z-[200] flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-slate-800/60 backdrop-blur-sm animate-fade-in"></div>
            
            <div class="relative bg-white rounded-2xl shadow-2xl max-w-130 w-full p-6 animate-scale-in">
                <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full mb-4" 
                    [ngClass]="{
                        'bg-red-100 text-red-600': config.type === 'error' || config.type === 'question', 
                        'bg-green-100 text-green-600': config.type === 'success',
                        'bg-amber-100 text-amber-600': config.type === 'warning'
                        }">
                    
                    <ng-icon *ngIf="config.type === 'question'" name="heroQuestionMarkCircleSolid" size="42px"></ng-icon>
                    <ng-icon *ngIf="config.type === 'error'" name="heroXCircleSolid" size="42px"></ng-icon>
                    <ng-icon *ngIf="config.type === 'success'" name="heroCheckCircleSolid" size="42px"></ng-icon>
                    <ng-icon *ngIf="config.type === 'warning'" name="heroExclamationTriangleSolid" size="42px"></ng-icon>
                </div>

                <div class="text-center">
                    <h3 class="text-xl font-black text-gray-800 uppercase">{{ config.title }}</h3>
                    <p class="text-sm text-gray-500 mt-2 font-sans whitespace-pre-line" [innerHTML]="config.message"></p>
                </div>

                <div class="mt-6 flex gap-3">
                    <button (click)="handleAction(true)" class="flex-1 bg-slate-900 text-white font-bold py-3 rounded-xl hover:bg-black transition-all">
                        {{ config.confirmText || 'ACEPTAR' }}
                    </button>
                    <button *ngIf="config.type === 'question'" (click)="handleAction(false)" class="flex-1 bg-gray-100 text-gray-600 font-bold py-3 rounded-xl hover:bg-gray-200 transition-all">
                        {{ config.cancelText || 'CANCELAR' }}
                    </button>
                </div>
            </div>
        </div>
    `
    })

export class AlertPriContainerComponent {
    private alertService = inject(AlertPriService);
    isOpen = false;
    config!: AlertOptions;
    private resolveFn!: (val: boolean) => void;

    constructor() {
        this.alertService.alertState$.subscribe(data => {
            this.config = data.options;
            this.resolveFn = data.resolve;
            this.isOpen = true;
        });
    }

    handleAction(value: boolean) {
        this.isOpen = false;
        this.resolveFn(value);
    }
}