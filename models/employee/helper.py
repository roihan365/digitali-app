from odoo import models

class HrEmployeeHelper(models.AbstractModel):
    _name = 'digitaliz.employee'

    def get_employee(self, employee_id):
        employee = self.env['hr.employee'].sudo().browse(employee_id)

        return [
            {
                'id': employee.id,
                # 'user_id': employee.user_id.id if employee.user_id else None,
                'name': employee.name,
                'email': employee.work_email,
                'phone': employee.work_phone,
                'company': employee.company_id.name if employee.company_id else None,
                'department': employee.department_id.name if employee.department_id else None,
                'position': employee.job_id.name if employee.job_id else None,
            }
        ]
        
    def get_all_employee(self):
        employees = self.env['hr.employee'].sudo().search([])
        
        return [
            {
                'id': employee.id,
                # 'user_id': employee.user_id.id if employee.user_id else None,
                'name': employee.name,
                'email': employee.work_email,
                'phone': employee.work_phone,
                'company': employee.company_id.name if employee.company_id else None,
                'department': employee.department_id.name if employee.department_id else None,
                'position': employee.job_id.name if employee.job_id else None,
            } 
            for employee in employees
        ]
