from odoo import http
from odoo.http import request
import json
from ..utils.cors import CorsHelper

class ApiEmployeeController(http.Controller):

    @http.route('/api/employee', type='http', auth='apikey', methods=['GET', 'OPTIONS'], csrf=False)
    def get_all_employees(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({}),
                headers=CorsHelper.cors_headers()
            )

        try:
            employees = request.env['digitaliz.employee'].get_all_employee()
            if employees:
                return request.make_response(
                    json.dumps({
                        'status': 'success',
                        'data': employees
                    }),
                    headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers()
                )
                
            else:
                return request.make_response(
                    json.dumps({
                        'status': 'error',
                        'message': 'No Employee Data'
                    }),
                    headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                    status=404
                )

        except Exception as e:
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': str(e)
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers()
            )

    @http.route('/api/employee/update', type='http', auth='apikey', methods=['PUT'], csrf=False)
    def update_employee(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(json.dumps({}), headers=CorsHelper.cors_headers())
        
        data = request.httprequest.data
        try:
            """
            values: {
                "name",
                "work_email",
                "work_phone",
                "department_id
            }"""
            json_data = json.loads(data)
            employee_id = json_data.get('employee_id')
            values = json_data.get('values', {})

            if not employee_id or not values:
                return request.make_response(
                    json.dumps({
                    'status': 'error',
                    'message': 'Employee ID dan values diperlukan.',
                }), headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                    status=400
                )

            # Cari employee berdasarkan ID
            employee = request.env['hr.employee'].sudo().browse(employee_id)
            if not employee.exists():
                return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': f'Employee dengan ID {employee_id} tidak ditemukan.',
                }),
                    headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                    status=400
                )

            # Update employee
            employee.sudo().write(values)
            return request.make_response(
                json.dumps({
                'status': 'success',
                'message': f'Employee dengan ID {employee_id} berhasil diupdate.',
            }), headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers()
            )
        except Exception as e:
            return request.make_response(
                json.dumps({
                'status': 'error',
                'message': f'Error: {str(e)}',
            }), headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )