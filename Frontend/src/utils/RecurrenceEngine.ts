import { RRule, Frequency } from 'rrule';
import type { RecurrenceRule, Appointment } from '../types/appointments';

export class RecurrenceEngine {
    static generateOccurrences(
        baseAppointment: Appointment,
        startDate: Date,
        endDate: Date
    ): Appointment[] {
        if (!baseAppointment.es_recurrente || !baseAppointment.regla_recurrencia) {
            return [baseAppointment];
        }

        const rule = this.createRRule(baseAppointment, startDate);
        const occurrences = rule.between(startDate, endDate, true);

        return occurrences.map((date, index) => {
            const duration = new Date(baseAppointment.end).getTime() - new Date(baseAppointment.start).getTime();
            const newStart = date;
            const newEnd = new Date(date.getTime() + duration);

            return {
                ...baseAppointment,
                id: index === 0 ? baseAppointment.id : `${baseAppointment.serie_id || baseAppointment.id}-${date.getTime()}`,
                start: newStart,
                end: newEnd,
                fecha_hora_inicio: newStart,
                fecha_hora_fin: newEnd,
            };
        });
    }

    private static createRRule(appointment: Appointment, dtstart: Date): RRule {
        const rule = appointment.regla_recurrencia!;

        const options: any = {
            freq: this.mapFrequency(rule.frequency),
            dtstart: new Date(appointment.start),
            interval: rule.interval || 1,
        };

        if (rule.count) {
            options.count = rule.count;
        } else if (rule.until || appointment.fecha_fin_recurrencia) {
            options.until = rule.until || appointment.fecha_fin_recurrencia;
        }

        if (rule.byweekday && rule.byweekday.length > 0) {
            options.byweekday = rule.byweekday;
        }

        return new RRule(options);
    }

    private static mapFrequency(freq: string): Frequency {
        const map: { [key: string]: Frequency } = {
            'DAILY': RRule.DAILY,
            'WEEKLY': RRule.WEEKLY,
            'MONTHLY': RRule.MONTHLY,
            'YEARLY': RRule.YEARLY,
        };
        return map[freq] || RRule.WEEKLY;
    }

    static formatRecurrenceText(rule: RecurrenceRule): string {
        const freqText: { [key: string]: string } = {
            'DAILY': 'Diariamente',
            'WEEKLY': 'Semanalmente',
            'MONTHLY': 'Mensualmente',
            'YEARLY': 'Anualmente',
        };

        let text = freqText[rule.frequency] || 'Personalizado';

        if (rule.interval && rule.interval > 1) {
            text = `Cada ${rule.interval} ${rule.frequency === 'DAILY' ? 'días' :
                    rule.frequency === 'WEEKLY' ? 'semanas' :
                        rule.frequency === 'MONTHLY' ? 'meses' : 'años'
                }`;
        }

        if (rule.count) {
            text += ` (${rule.count} veces)`;
        }

        return text;
    }
}
