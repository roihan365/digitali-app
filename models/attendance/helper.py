from odoo import models, fields, _
from odoo.tools import float_round
from odoo.http import request
import math
import datetime

class HrAttendance(models.Model):
    _name = 'digitaliz.attendance'

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two lat/long pairs using Haversine formula."""
        R = 6371000  # Radius of Earth in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi / 2.0)**2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2.0)**2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    def get_geoip_response(self, mode, latitude=False, longitude=False):
        """Generate geo-IP response."""
        geoip = request.geoip
        http_request = request.httprequest

        return {
            'city': geoip.city.name or _('Unknown') if geoip.city else _('Unknown'),
            'country_name': geoip.country.name or geoip.continent.name or _('Unknown') if geoip.country else _('Unknown'),
            'latitude': latitude or (geoip.location.latitude if geoip.location else False),
            'longitude': longitude or (geoip.location.longitude if geoip.location else False),
            'ip_address': geoip.ip if geoip else 'Unknown',
            'browser': http_request.user_agent.browser,
            'mode': mode
        }

    @staticmethod
    def get_user_attendance_data(employee):
        """Return user's attendance data."""
        response = {}
        if employee:
            response = {
                'id': employee.id,
                'hours_today': float_round(employee.hours_today, precision_digits=2),
                'hours_previously_today': float_round(employee.hours_previously_today, precision_digits=2),
                'last_attendance_worked_hours': float_round(employee.last_attendance_worked_hours, precision_digits=2),
                'last_check_in': employee.last_check_in.isoformat() if employee.last_check_in else None,
                'attendance_state': employee.attendance_state,
                'display_systray': employee.company_id.attendance_from_systray,
            }
        return response

    @staticmethod
    def get_employee_info_response(employee):
        """Return employee information response."""
        response = {}
        if employee:
            response = {
                **HrAttendance.get_user_attendance_data(employee),
                'employee_name': employee.name,
                'total_overtime': float_round(employee.total_overtime, precision_digits=2),
                'kiosk_delay': employee.company_id.attendance_kiosk_delay * 1000,
                'attendance': {
                    'check_in': employee.last_attendance_id.check_in.isoformat() if employee.last_attendance_id.check_in else None,
                    'check_out': employee.last_attendance_id.check_out.isoformat() if employee.last_attendance_id.check_out else None,
                },
                'overtime_today': request.env['hr.attendance.overtime'].sudo().search([
                    ('employee_id', '=', employee.id), 
                    ('date', '=', datetime.date.today()),
                    ('adjustment', '=', False)
                ]).duration or 0,
                'use_pin': employee.company_id.attendance_kiosk_use_pin,
                'display_overtime': employee.company_id.hr_attendance_display_overtime
            }
        return response