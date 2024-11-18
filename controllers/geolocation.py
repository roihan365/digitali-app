from odoo import http, _
from odoo.http import request
import json
from ..utils.cors import CorsHelper

class AttendanceAPIController(http.Controller):

    @http.route('/api/attendance/check_in', type='http', auth='tokenUnit', methods=['POST'], csrf=False)
    def check_in_attendance(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(json.dumps({}), headers=CorsHelper.cors_headers())
        
        data = request.httprequest.data

        try:
            json_data = json.loads(data)
            latitude = json_data.get('latitude')
            longitude = json_data.get('longitude')
            office_lat = json_data.get('office_lat')
            office_long = json_data.get('office_long')
            employee_id = json_data.get('employee_id')
            type = json_data.get('type')
        except (ValueError, TypeError):
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Invalid JSON format.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )

        if latitude is None or longitude is None:
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Latitude and Longitude are required.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )
        
        if office_lat is None or office_long is None:
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Office Latitude and Longitude are required.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )
        if employee_id is None:
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Employee ID is required.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )
        if type is None:
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Type Attendance is required.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )

        # start record attendance
        employee = request.env['hr.employee'].sudo().browse(employee_id)
        if not employee.exists():
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'User is not linked to any employee'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=404
            )
            
        if type == "normal":
            distance = request.env['digitaliz.attendance'].calculate_distance(latitude, longitude, office_lat, office_long)
            if distance >= 550:
                return request.make_response(
                    json.dumps({
                        'status': 'error',
                        'message': f'You are too far from the office. Distance: {distance:.2f} meters'
                    }),
                    headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                    status=400
                )

        geo_ip_response = request.env['digitaliz.attendance'].get_geoip_response(
            mode='systray', latitude=latitude, longitude=longitude
        )
        employee._attendance_action_change(geo_ip_response)
        data = request.env['digitaliz.attendance'].get_employee_info_response(employee)
        
        return request.make_response(
            json.dumps({
                'status': 'success',
                'message': 'Attendance today recorded',
                'data': data
            }),
            headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
            status=200
        )