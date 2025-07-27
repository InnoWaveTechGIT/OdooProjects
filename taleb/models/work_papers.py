from odoo import models,api, fields,_
import os
import time
import base64
from odoo.exceptions import ValidationError

def _abs_rout(self,data):
    path1=''
    abs = os.path.dirname(os.path.abspath(__file__))
    abs_sp =abs.split("/")
    for i in abs_sp:
        if i !='models':
            path1 += i +'/'
    return path1
    

class WhyUsTaleb(models.Model):
    _name = 'work.papers.taleb'
    _description = "this module is for work.papers.taleb"
    _rec_name = 'title'
    _order = 'order asc'


    title = fields.Char(string='Title')
    course_id = fields.Many2one('courses' , string='Course' ,required = True ,ondelete='cascade')
    section_id = fields.Many2one('section' , string ='section' ,required = True,domain="[('course_id', '=', course_id)]")
    order = fields.Integer(string='Order')
    work_paper_ids = fields.One2many('work.papers.line.taleb' , 'work_id' , string='Work Papers')


class WhyUsTaleb(models.Model):
    _name = 'work.papers.line.taleb'
    _description = "this module is for work.papers.taleb"
    _rec_name = 'title'
    _order = 'order asc'

    title = fields.Char(string='Title' ,required=True)
    work_id = fields.Many2one('work.papers.taleb')
    question = fields.Binary(string='Question' ,required=True)
    question_file_name = fields.Char('question file name')
    question_path = fields.Char('question path')
    answer = fields.Binary(string='Answer' ,required=True)
    answer_file_name = fields.Char('answer file name')
    answer_path = fields.Char('answer path')
    order = fields.Integer(string='Order')


    def open_comments(self):
        orders = self.env['work.papers.enquery.taleb'].search([('work_id' , '=' , self.id)])
        
        action = {
            'res_model': 'work.papers.enquery.taleb',
            'type': 'ir.actions.act_window'
        }
        
       
        action.update({
            'name': _("Comments"),
            'domain': [('id', 'in', orders.ids)],
            'view_mode': 'tree,form'
        })
        return action

    @api.model
    def create(self, vals):
        data = os.path.dirname(os.path.abspath(__file__))
        print('vals' , vals["question_file_name"])
        print('question' , vals["question"])
        if "question_file_name" in vals and "question" in vals :
            try:
                print('Yes')
        
                image_type = vals['question_file_name'].split(".") 
                print('image_type' , image_type)
                types =['pdf' , 'PDF' , 'Pdf']
                if image_type[-1] in types :
                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/work_papers"#loc
            
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                    with open(os.path.join(module_path, time_stamp + vals["question_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["question"]))
                    
                    vals["question_path"] = "/taleb/static/work_papers/" + \
            time_stamp + vals["question_file_name"].replace(" ", "")
                else:
                     raise ValidationError(_("Only PDF Files"))
            except Exception as e:
                pass

            
            
        if "answer_file_name" in vals and "answer" in vals:
            try:
                image_type = vals['question_file_name'].split(".") 
                types =['pdf' , 'PDF' , 'Pdf']
                if image_type[-1] in types :
                    time_stamp = str(time.time())
                    module_path = _abs_rout(self ,data)+"static/work_papers"#loc
            
                    isExist = os.path.exists(module_path)
                    if isExist == False:
                        os.mkdir(module_path)
                    with open(os.path.join(module_path, time_stamp + vals["answer_file_name"].replace(" ", "")), "wb+") as f:
                        f.write(base64.b64decode(vals["answer"]))

                    vals["answer_path"] = "/taleb/static/work_papers/" + \
            time_stamp + vals["answer_file_name"].replace(" ", "")
                else:
                     raise ValidationError(_("Only PDF Files"))
            except Exception as e:
                pass

            
            
        values=super().create(vals)
        return values

    
class WhyUsTaleb(models.Model):
    _name = 'work.papers.enquery.taleb'
    _description = "this module is for work.papers.enquery.taleb"
    _rec_name = 'work_id'

    work_id = fields.Many2one('work.papers.line.taleb' , string='Work Paper')
    user_id = fields.Many2one('res.users' , string='User')
    section_id = fields.Many2one('section' , string='Section'  ,ondelete='cascade')
    course_id = fields.Many2one('courses' , string='Course'  ,ondelete='cascade' )
    comment_ids = fields.One2many('work.papers.enquery.line.taleb' , 'replay_id' , string='Replaies')
    image_ids = fields.One2many('comment.images.workpaper' , 'comment_id' , string='Images')
    comment = fields.Text(string='Comment')
    pending=fields.Boolean(default=True)

    @api.constrains('comment_ids')
    def set_teacher_id(self):
        for rec in self:
            if len(rec.comment_ids) == 0:
                rec.pending = True
    @api.model
    def create(self, vals):
        if vals['work_id']:
            work_id = self.env['work.papers.line.taleb'].search([('id' , '=' ,int(vals['work_id']))])
            vals['course_id'] = work_id.work_id.course_id.id
            vals['section_id'] = work_id.work_id.section_id.id
        values=super().create(vals)
        
        return values

    # def write(self, vals):
    #     print('vals >>> ' , vals)
    #     print(self.id)
        
    #     work_id = self.env['work.papers.enquery.taleb'].search([('id' , '=' ,self.id)])
    #     print(work_id)
    #     vals['course_id'] = work_id.work_id.work_id.course_id.id
    #     vals['section_id'] = work_id.work_id.work_id.section_id.id

    #     return super().write(vals)
    @api.constrains('work_id')
    def set_teacher_id(self):
        for rec in self : 
            rec.update({
                'course_id' : rec.work_id.work_id.course_id.id,
                'section_id' : rec.work_id.work_id.section_id.id
                })
class EnquiryTaleb(models.Model):
    # make notfication to commented user 
    _name = 'comment.images.workpaper'
    _description = "this module is for testing purpose only, it was created by Eng Ali Ammar"

    comment_id = fields.Many2one('work.papers.enquery.taleb')
    
    image=fields.Binary(string='Image')
    image_url = fields.Char("image url", compute='_compute_image_url')

    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image:
                obj.image_url= base_url + '/web/image?' + 'model=comment.images.workpaper&id=' + str(obj.id) + '&field=image'
            else :
                obj.image_url= ''

class WhyUsTaleb(models.Model):
    _name = 'work.papers.enquery.line.taleb'
    _description = "this module is for work.papers.enquery.taleb"
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users' , string='User', default=lambda self: self.env.user)
    comment = fields.Text(string='Comment' ,required=True)
    replay_id = fields.Many2one('work.papers.enquery.taleb' , string='Replay')
    image_1 = fields.Binary('image one')
    image_2 = fields.Binary('image Two')
    image_3 = fields.Binary('image Three')
    image_4 = fields.Binary('image Four')
    image_5 = fields.Binary('image Five')
    image_url1 = fields.Char("image url", compute='_compute_image_url')
    image_url2 = fields.Char("image url", compute='_compute_image_url2')
    image_url3 = fields.Char("image url", compute='_compute_image_url3')
    image_url4 = fields.Char("image url", compute='_compute_image_url4')
    image_url5 = fields.Char("image url", compute='_compute_image_url5')


    @api.depends('image_1')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image_1:
                obj.image_url1= base_url + '/web/image?' + 'model=work.papers.enquery.line.taleb&id=' + str(obj.id) + '&field=image_1'
            else :
                obj.image_url1= ''
    @api.depends('image_2')
    def _compute_image_url2(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image_2:
                obj.image_url2= base_url + '/web/image?' + 'model=work.papers.enquery.line.taleb&id=' + str(obj.id) + '&field=image_2'
            else :
                obj.image_url2= ''
    
    @api.depends('image_3')
    def _compute_image_url3(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image_3:
                obj.image_url3= base_url + '/web/image?' + 'model=work.papers.enquery.line.taleb&id=' + str(obj.id) + '&field=image_3'
            else :
                obj.image_url3= ''
    
    @api.depends('image_4')
    def _compute_image_url4(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for obj in self:
            if obj.image_4:
                obj.image_url4= base_url + '/web/image?' + 'model=work.papers.enquery.line.taleb&id=' + str(obj.id) + '&field=image_4'
            else :
                obj.image_url4= ''
    
    @api.depends('image_5')
    def _compute_image_url5(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print('base_url' , base_url)
        for obj in self:
            if obj.image_5:
                obj.image_url5= base_url + '/web/image?' + 'model=work.papers.enquery.line.taleb&id=' + str(obj.id) + '&field=image_5'
            else :
                obj.image_url5= ''
    
    @api.model
    def create(self, vals):

        values =super().create(vals)
        session_id=self.env['work.papers.enquery.taleb'].search([('id','=',vals['replay_id'])])
        
        
        if len(session_id.comment_ids)>1:
            raise ValidationError("تم الأجابة على هذا السؤال مسبقا")
            
        
        session_id.pending=False
    #     dt = session_id.user_id
        
    #     user_type=self.env['res.users'].search([('id','=',self.env.user.id)])
    #     user_type=user_type.user_type
        
    #     if (user_type!='teacher'):
    #         raise ValidationError("يجب ان تسجل من حساب أستاذ لتتمكن من الأجابة")
            
    #     token =self.env['user.token'].sudo().search([('user_id','=',dt.id)])
    #     f_token = token.fire_base
    #     reply_id = values.id
    #     session_title = session_id.enquiry_id.Title
    #     comment_id = vals['replay_id']
    #     course_id =session_id.course_id['id']
    #     course=self.env['courses'].search([('id','=',int(course_id))])
    #     course_title=course.name
    #     video =session_id.enquiry_id['id']
    #     section=self.env['course.video'].search([('id','=',video)])
    #     comment_user=session_id.user_id['id']
        
    #     user_name =values.user_id['name']
    #     comment = values.comment
    #     session_id=session_id.enquiry_id.id
    #     title ='قام %s بالرد على تعليقك' %(user_name)
    #     payload = {
    #     "comment_id":comment_id,
    #     "session_id":session_id,
    #     "session_title" : session_title,
    #     "course_id":course_id,
    #     "reply_id":reply_id,
    #     'title' :title,
    #     'section_id':section.id,
    #     'course_title':course_title,

    #     "comment":comment,
    #     "notification_type":"Comment"
    # }
    #     noti_data={
    #         'user_id':comment_user,
    #         'data':payload,
    #         'notification_type':"Comment"
    #     }
    #     self.env['notifications'].sudo().create(noti_data)
    #     send_notification.send_notification(self,f_token,payload)

    #     mail_activity = self.env['mail.activity'].sudo().search([('res_id' , '=' ,values.replay_id.id )])
    #     mail_activity.action_feedback(feedback="good job!")
        return values