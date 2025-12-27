// Notification Service for Reminders
export class NotificationService {
    private static instance: NotificationService;
    private scheduledNotifications: Map<string, number> = new Map();

    private constructor() {
        this.requestPermission();
    }

    static getInstance(): NotificationService {
        if (!NotificationService.instance) {
            NotificationService.instance = new NotificationService();
        }
        return NotificationService.instance;
    }

    async requestPermission(): Promise<boolean> {
        if (!('Notification' in window)) {
            console.warn('Este navegador no soporta notificaciones');
            return false;
        }

        if (Notification.permission === 'granted') {
            return true;
        }

        if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }

        return false;
    }

    scheduleReminder(appointmentId: string, title: string, time: Date, message: string): void {
        const now = new Date().getTime();
        const reminderTime = time.getTime();
        const delay = reminderTime - now;

        if (delay <= 0) {
            return; // Ya pasó el tiempo
        }

        // Cancelar notificación previa si existe
        this.cancelReminder(appointmentId);

        const timeoutId = window.setTimeout(() => {
            this.showNotification(title, message);
            this.scheduledNotifications.delete(appointmentId);
        }, delay);

        this.scheduledNotifications.set(appointmentId, timeoutId);
    }

    cancelReminder(appointmentId: string): void {
        const timeoutId = this.scheduledNotifications.get(appointmentId);
        if (timeoutId) {
            clearTimeout(timeoutId);
            this.scheduledNotifications.delete(appointmentId);
        }
    }

    private async showNotification(title: string, body: string): Promise<void> {
        const hasPermission = await this.requestPermission();
        if (!hasPermission) return;

        new Notification(title, {
            body,
            icon: '/favicon.ico',
            badge: '/favicon.ico',
            tag: 'podoskin-reminder',
            requireInteraction: false,
        });
    }

    cancelAll(): void {
        this.scheduledNotifications.forEach((timeoutId) => clearTimeout(timeoutId));
        this.scheduledNotifications.clear();
    }
}

export default NotificationService.getInstance();
