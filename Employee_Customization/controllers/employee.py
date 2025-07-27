from odoo import http
import json
from odoo.http import request ,Response



class EmployeeController(http.Controller):

    @http.route('/api/set_over_time', auth='public', methods=['POST'], csrf=False, type='http')
    def set_over_time(self,employee_id =None, **params):
        if employee_id:
            employee_id = int(employee_id)
        else:
            message = 'please send employee id'
            response = json.dumps({'data': [] ,'message': message, 'is_success' :False})
            return Response(
                response, status=401, content_type='application/json'
            )
        employee = request.env['hr.employee'].sudo().search([('id' , '=' , employee_id)])
        if employee:
            employee.overtime_ability = True
        else:
            message = 'please send valid (exist) employee id'
            response = json.dumps({'data': [] ,'message': message, 'is_success' :False})
            return Response(
                response, status=404, content_type='application/json'
            )
        message = 'The process is done this employee overtime ability is true now'
        response = json.dumps({'data': [] , 'message' : message , 'is_success' :True})
        return Response(
            response, status=200, content_type='application/json'
        )

    @http.route('/api/get_over_time', auth='public', methods=['GET'], csrf=False, type='http')
    def get_over_time(self,employee_id =None, **params):
        if employee_id:
            employee_id = int(employee_id)
        else:
            message = 'please send employee id'
            response = json.dumps({'data': [] ,'message': message, 'is_success' :False})
            return Response(
                response, status=401, content_type='application/json'
            )
        employee = request.env['hr.employee'].sudo().search([('id' , '=' , employee_id)])
        if employee:
            employee_over_time  = employee.overtime_ability
        else:
            message = 'please send valid (exist) employee id'
            response = json.dumps({'data': [] ,'message': message, 'is_success' :False})
            return Response(
                response, status=404, content_type='application/json'
            )
        message = 'The process is done this employee overtime ability is true now'
        response = json.dumps({'data': {'name':employee.name , 'over_time_ability': employee.overtime_ability} , 'message' : message , 'is_success' :True})
        return Response(
            response, status=200, content_type='application/json'
        )
