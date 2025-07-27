from odoo import models,api, fields,_


class UserSessionStatus(models.Model):
    _name = 'session_status'
    _description = "this module is for session_status"
    _rec_name='user_id'
    
    user_id= fields.Many2one('res.users' ,string='الطالب')
    session_id = fields.Many2one('course.video' ,string='اسم الجلسة')
    section_name = fields.Many2one('section' ,string='اسم الوحدة', related='session_id.section_id', store=True)
    course_name = fields.Many2one('courses', string='اسم الكورس', related='session_id.course_id', store=True)
    is_watched = fields.Boolean('Watched')
    section_count = fields.Float('تقدم الوحدة' , compute='_get_section_progress' )
    course_count = fields.Float('تقدم الكورس' , compute='_get_course_progress' )
    active = fields.Boolean(default=True)

    session_question_count = fields.Integer('Question Count' , compute='get_questin_and_grad' )
    user_course_mark = fields.Float('Course Mark', compute='get_questin_and_grad' )
    user_session_comment = fields.Char('Session Comment' )
    user_session_rate = fields.Float('Session Rate')
    progress = fields.Float('تقدم الفيديو')
    subscribed = fields.Selection([('subscribed', 'مشترك'),
                              ('unsubscribed', 'غير مشترك')], required=True, default='unsubscribed', string="Subscription", compute="compute_subscription")
    courses_dont_have_session = fields.Char(string="المواد التي لم يتم حضورها", compute="compute_courses_dont_have_session")

    @api.depends('user_id')
    def compute_courses_dont_have_session(self):
        for rec in self:
            rec.courses_dont_have_session = ''
            session_ids = self.env['session_status'].search([('user_id', '=', rec.user_id.id)])
            if session_ids:
                user_session_courses = session_ids.mapped('course_name')
                if user_session_courses:
                    for course in rec.user_id.student_course_ids.filtered(lambda course: course not in user_session_courses):
                        rec.courses_dont_have_session += course.name + ', '


    @api.depends('user_id', 'course_name')
    def compute_subscription(self):
        for rec in self:
            subscription_id = self.env['subscription'].search([('user_id', '=', rec.user_id.id), ('course_id', '=', rec.course_name.id)])
            if subscription_id:
                rec.subscribed = 'subscribed'
            else:
                rec.subscribed = 'unsubscribed'

    @api.depends('user_id')
    def get_questin_and_grad(self):
        for rec in self:
            comments = self.env['enquiries'].search_count([('user_id' , '=' ,rec.user_id.id),('enquiry_id' , '=' ,rec.session_id.id)])
            rec.update({
                'session_question_count' : comments
            })
            print('**************************************************************************')
            user_mark = self.env['course.result'].search([('course_result_id' ,'=' , rec.user_id.id) ,('course_id' , '=' ,rec.course_name.id)], limit=1)
            if user_mark:
                rec.update({
                'user_course_mark' : user_mark.result
            })
            else:
                rec.update({
                'user_course_mark' : 0
            })
            # rate = self.env['video_rate.value'].search([('user_id' ,'=' , rec.user_id.id)])
            # print('>>>>>>>>>>> rate ' , rate)
            # for item in rate :
            #     if item.rate_id.video.id == rec.session_id.id:
            #         rec.update({
            #     'user_session_comment' : item.comment,
            #     'user_session_rate' : item.rataing
            # })
            #     else:
            #         rec.update({
            #     'user_session_comment' : '',
            #     'user_session_rate' : 0.0
            # })


    
    @api.depends('is_watched')
    def _get_section_progress(self):
        for rec in self:
            prog = 0.0
            sections = self.env['course.video'].search_count([('section_id' , '=' , rec.section_name.id)])
            if sections != 0:
                prog = round((1/sections) * 100 , 2)
                rec.update({
                    'section_count' : prog
                })
            else:
                rec.update({
                    'section_count' : 0
                })
    @api.depends('is_watched')
    def _get_course_progress(self):
        for rec in self:
            prog = 0.0
            sections = self.env['course.video'].search_count([('course_id' , '=' , rec.course_name.id)])
            if sections != 0:
                prog = round((1/sections) * 100 , 2)
                rec.update({
                    'course_count' : prog
                })
            else:
                rec.update({
                    'course_count' : 0
                })
            
        



class UserCoursesStatus(models.Model):
    _name = 'course_status'
    _description = "this module is for testing purpose only, it was created by Eng Ali Ammar"
    _rec_name='user_id'
    
    user_id= fields.Many2one('res.users' ,string='User Name')
    course_id = fields.Many2one('courses' ,string='Course Name')
    is_watched = fields.Boolean('Watched')
    active = fields.Boolean(default=True)


class UserSectionsStatus(models.Model):
    _name = 'section_status'
    _description = "this module is for testing purpose only, it was created by Eng Ali Ammar"
    _rec_name='user_id'
    
    user_id= fields.Many2one('res.users' ,string='User Name')
    section_id = fields.Many2one('section' ,string='Section Name')
    course_name = fields.Many2one('courses', string='Course Name', related='section_id.course_id', store=True)
    is_watched = fields.Boolean('Watched')
    active = fields.Boolean(default=True)