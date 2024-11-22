from odoo import http, fields , _
from odoo.http import request
import json
from datetime import datetime
from ..utils.cors import CorsHelper

class AttendanceAPIController(http.Controller):

    @http.route('/api/leaves/action', type='http', auth='apikey', methods=['POST'], csrf=False)
    def leave_action(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(json.dumps({}), headers=CorsHelper.cors_headers())
        
        data = request.httprequest.data

        try:
            json_data = json.loads(data)
            id = json_data.get('leave_id')
            action = json_data.get('action')
        except (ValueError, TypeError):
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Invalid JSON format.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )

        if id is None or id == '':
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Leave ID is required.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )
            
        if action is None or action == '' or action not in ['approve', 'refuse']:
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Action is required or invalid.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )

        # Cari record cuti berdasarkan leave_id
        leave_record = request.env['hr.leave'].browse(id)

        # Periksa apakah leave_id valid
        if not leave_record.exists():
            return request.make_response(
                json.dumps({
                    'status': 'error', 
                    'message': 'Leave record not found'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=404
            )
        
        # Pastikan status cuti masih bisa disetujui
        if leave_record.state != 'confirm':
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Leave cannot be approved in its current state'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )
        
        try:
            if (action == 'approve'):
                leave_record.action_approve()
            elif (action == 'refuse'):
                leave_record.action_refuse()
            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'message': f'Leave {action} successfully executed'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=200
            )
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/leaves', type='http', auth='apikey', methods=['POST'], csrf=False)
    def leave_request(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(json.dumps({}), headers=CorsHelper.cors_headers())
        
        data = request.httprequest.data

        try:
            json_data = json.loads(data)
            employee_id = json_data.get('employee_id')
            leave_type = json_data.get('leave_type')
            date_from = json_data.get('date_from')
            date_to = json_data.get('date_to')
            reason = json_data.get('reason')
        except (ValueError, TypeError):
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Invalid JSON format.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )

        if employee_id is None or employee_id == '':
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Employee ID is required.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )
            
        if leave_type is None or leave_type == '':
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Leave type is required.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )

        if date_from is None or date_from == '':
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Date from is required.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )

        if date_to is None or date_to == '':
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Date to is required.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )

        if reason is None or reason == '':
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Reason is required.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )

        # Cari record employee berdasarkan employee_id
        employee_record = request.env['hr.employee'].browse(employee_id)

        # Periksa apakah employee_id valid
        if not employee_record.exists():
            return request.make_response(
                json.dumps({
                    'status': 'error', 
                    'message': 'Employee record not found'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=404
            )
            
        try:
            start_date = fields.Datetime.from_string(date_from)
            end_date = fields.Datetime.from_string(date_to)
            
            leave_record = request.env['hr.leave'].sudo().create({
                'employee_id': employee_id,
                'holiday_status_id': leave_type,
                'request_date_from': start_date,
                'request_date_to': end_date,
                'name': reason,
                'state': 'confirm',
            })

            # Extract relevant fields from the leave record for JSON serialization
            leave_data = {
                'id': leave_record.id,
                'employee_id': leave_record.employee_id.id,
                'holiday_status_id': leave_record.holiday_status_id.id,
                'request_date_from': leave_record.request_date_from.strftime('%Y-%m-%d') if leave_record.request_date_from else None,
                'request_date_to': leave_record.request_date_to.strftime('%Y-%m-%d') if leave_record.request_date_to else None,
                'name': leave_record.name,
                'state': leave_record.state,
            }

            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'message': 'Leave request successfully created',
                    'data': leave_data
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=200
            )
        except Exception as e:
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': str(e)
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )
        
    @http.route('/api/leaves', type='http', auth='apikey', methods=['GET'], csrf=False)
    def get_leave_requests(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(json.dumps({}), headers=CorsHelper.cors_headers())
        
        leave_requests = request.env['hr.leave'].search([])

        if not leave_requests:
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'data': []
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=404
            )

        result = []
        for leave_request in leave_requests:
            result.append({
                'id': leave_request.id,
                'employee_id': leave_request.employee_id.id,
                'employee_name': leave_request.employee_id.name,
                'reason': leave_request.name,
                'number_of_days': leave_request.number_of_days,
                'department_id': leave_request.department_id.id if leave_request.department_id else None,
                'department_name': leave_request.department_id.name if leave_request.department_id else None,
                'category_id': leave_request.category_id.id if leave_request.category_id else None,
                'category_name': leave_request.category_id.name if leave_request.category_id else None,
                'time_off_type': leave_request.holiday_status_id.name if leave_request.holiday_status_id else None,
                'status': leave_request.state,
                'allocation_mode': leave_request.holiday_type,
                'date_from': leave_request.date_from.isoformat() if leave_request.date_from else None,
                'date_to': leave_request.date_to.isoformat() if leave_request.date_to else None,
                'company_id': leave_request.company_id.id if leave_request.company_id else None,
                'company_name': leave_request.company_id.name if leave_request.company_id else None
            })

        return request.make_response(
            json.dumps({
                'status': 'success',
                'data': result
            }),
            headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
            status=200
        )
        
    @http.route('/api/leaves/<int:employee_id>', type='http', auth='apikey', methods=['GET'], csrf=False)
    def get_leave_employee_request(self, employee_id, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(json.dumps({}), headers=CorsHelper.cors_headers())
            
        if employee_id is None or employee_id == '':
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Employee ID is required.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=400
            )
            
        # Cari record employee berdasarkan employee_id
        employee_record = request.env['hr.employee'].browse(employee_id).exists()

        # Periksa apakah employee_id valid
        if not employee_record:
            return request.make_response(
                json.dumps({
                    'status': 'error', 
                    'message': 'Employee record not found'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=404
            )
            
        leave_requests = request.env['hr.leave'].search([('employee_id', '=', employee_id)])
        
        if not leave_requests:
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'data': []
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=404
            )
            
        result = []
        for leave_request in leave_requests:
            result.append({
                'id': leave_request.id,
                'employee_id': leave_request.employee_id.id,
                'employee_name': leave_request.employee_id.name,
                'reason': leave_request.name,
                'number_of_days': leave_request.number_of_days,
                'department_id': leave_request.department_id.id if leave_request.department_id else None,
                'department_name': leave_request.department_id.name if leave_request.department_id else None,
                'category_id': leave_request.category_id.id if leave_request.category_id else None,
                'category_name': leave_request.category_id.name if leave_request.category_id else None,
                'time_off_type': leave_request.holiday_status_id.name if leave_request.holiday_status_id else None,
                'status': leave_request.state,
                'allocation_mode': leave_request.holiday_type,
                'date_from': leave_request.date_from.isoformat() if leave_request.date_from else None,
                'date_to': leave_request.date_to.isoformat() if leave_request.date_to else None,
                'company_id': leave_request.company_id.id if leave_request.company_id else None,
                'company_name': leave_request.company_id.name if leave_request.company_id else None
            })
            
        return request.make_response(
            json.dumps({
                'status': 'success',
                'data': result
            }),
            headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
            status=200
        )
        
    @http.route('/api/leaves/type', type='http', auth='apikey', methods=['GET'], csrf=False)
    def get_leave_type(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(json.dumps({}), headers=CorsHelper.cors_headers())
        
        leave_types = request.env['hr.leave.type'].search([])

        if not leave_types:
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'Leave types not found.'
                }),
                headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
                status=404
            )

        result = []
        for leave_type in leave_types:
            result.append({
                'id': leave_type.id,
                'name': leave_type.name,
                'leave_type': leave_type.leave_validation_type
            })

        return request.make_response(
            json.dumps({
                'status': 'success',
                'data': result
            }),
            headers=[('Content-Type', 'application/json')] + CorsHelper.cors_headers(),
            status=200
        )