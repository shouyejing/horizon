# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 be-cloud.be
#                       Jerome Sonnet <jerome.sonnet@be-cloud.be>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from openerp import api, fields, models, _
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)

class Course(models.Model):
    '''Course'''
    _name = 'school.course'
    _description = 'Course'
    _inherit = ['mail.thread']
    
    code = fields.Char(required=True, string='Code', size=8)
    name = fields.Char(required=True, string='Name')
    description = fields.Text(string='Description')
    
    credits = fields.Integer(required=True, string = 'Credits')
    hours = fields.Integer(required=True, string = 'Hours')
    weight =  fields.Integer(string = 'Weight')
    
    notes = fields.Text(string='Notes')
    
    course_group_ids = fields.Many2many('school.course_group', 'school_course_course_group_rel', id1='course_id', id2='course_group_id', string='Course Groups', ondelete='set null')
    
class CourseGroup(models.Model):
    '''Courses Group'''
    _name = 'school.course_group'
    _description = 'Courses Group'
    _inherit = ['mail.thread']

    @api.one
    @api.depends('course_ids')
    def _get_courses_total(self):
        total_hours = 0.0
        total_credits = 0.0
        total_weight = 0.0
        for course in self.course_ids:
            total_hours += course.hours
            total_credits += course.credits
            total_weight += course.weight
        self.total_hours = total_hours
        self.total_credits = total_credits
        self.total_weight = total_weight

    code = fields.Char(required=True, string='Code', size=8)
    name = fields.Char(required=True, string='Name')
    year_id = fields.Many2one('school.year', string="Year", related='program_id.year_id', store=True)
    description = fields.Text(string='Description')
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')
    total_weight = fields.Integer(compute='_get_courses_total', string='Total Weight')
    
    notes = fields.Text(string='Notes')
    
    course_ids = fields.Many2many('school.course', 'school_course_course_group_rel', id1='course_group_id', id2='course_id', string='Courses', ondelete='set null')
    program_id = fields.Many2one('school.program', required=True, string='Program')
    
class Program(models.Model):
    '''Progral'''
    _name = 'school.program'
    _description = 'Program'
    _inherit = ['mail.thread']
    
    @api.one
    @api.depends('course_group_ids')
    def _get_courses_total(self):
        total_hours = 0.0
        total_credits = 0.0
        for course_group in self.course_group_ids:
            total_hours += course_group.total_hours
            total_credits += course_group.total_credits
        self.total_hours = total_hours
        self.total_credits = total_credits

    code = fields.Char(required=True, string='Code', size=8)
    name = fields.Char(required=True, string='Name')
    year_id = fields.Many2one('school.year', string="Year", related='bloc_id.year_id', store=True)
    description = fields.Text(string='Description')
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')

    notes = fields.Text(string='Notes')
    
    course_group_ids = fields.One2many('school.course_group', 'program_id', string='Courses Groups')

    bloc_id = fields.Many2one('school.bloc', required=True, string='Bloc')

class Bloc(models.Model):
    '''Bloc'''
    _name = 'school.bloc'
    _description = 'Bloc of Programs'
    _inherit = ['mail.thread']
    
    @api.one
    @api.depends('program_ids')
    def _get_courses_total(self):
        total_hours = 0.0
        total_credits = 0.0
        for program in self.program_ids:
            total_hours += program.total_hours
            total_credits += program.total_credits
        self.total_hours = total_hours
        self.total_credits = total_credits
    
    state = fields.Selection([
            ('draft','Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ], string='Status', index=True, readonly=True, default='draft',
        #track_visibility='onchange', TODO : is this useful for this case ?
        copy=False,
        help=" * The 'Draft' status is used when a new program is created and not published yet.\n"
             " * The 'Published' status is when a program is published and available for use.\n"
             " * The 'Archived' status is used when a program is obsolete and not publihed anymore.")
    
    code = fields.Char(required=True, string='Code', size=8)
    name = fields.Char(required=True, string='Name')
    year_id = fields.Many2one('school.year', required=True, string="Year")
    description = fields.Text(string='Description')
    
    competency_ids = fields.Many2many('school.competency','school_competency_bloc_rel', id1='bloc_id', id2='competency_id', string='Competencies', ondelete='set null')
    
    domain_id = fields.Many2one('school.domain', string='Domain')
    cycle_id = fields.Many2one('school.cycle', string='Cycle')
    section_id = fields.Many2one('school.section', string='Section')
    track_id = fields.Many2one('school.track', string='Track')
    speciality_id = fields.Many2one('school.speciality', string='Speciality')
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')

    notes = fields.Text(string='Notes')
    
    program_ids = fields.One2many('school.program', 'bloc_id', string='Programs')
    
    @api.multi
    def unpublish(self):
        return self.write({'state': 'draft'})
    
    @api.multi
    def publish(self):
        return self.write({'state': 'published'})
    
    @api.multi
    def archive(self):
        return self.write({'state': 'archived'})

class Competency(models.Model):
    '''Competency'''
    _name = 'school.competency'
    _order = 'sequence asc'
    sequence = fields.Integer(required=True, string='Sequence')
    description = fields.Text(string='Description')
    
    program_ids = fields.Many2many('school.program','school_competency_program_rel', id1='competency_id', id2='program_id', string='Programs', ondelete='set null')
    
class Domain(models.Model):
    '''Domain'''
    _name = 'school.domain'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    
class Cycle(models.Model):
    '''Cycle'''
    _name = 'school.cycle'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    
class Section(models.Model):
    '''Section'''
    _name = 'school.section'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    
class Track(models.Model):
    '''Track'''
    _name = 'school.track'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    
class Speciality(models.Model):
    '''Speciality'''
    _name = 'school.speciality'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    
class Year(models.Model):
    '''Year'''
    _name = 'school.year'
    name = fields.Char(required=True, string='Name', size=15)