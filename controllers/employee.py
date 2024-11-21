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
