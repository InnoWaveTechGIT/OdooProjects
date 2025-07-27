# Copyright 2021 Tecnativa - Jairo Llopis
# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from dateutil.parser import isoparse

from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.http import request, route
from odoo.tests.common import Form

from odoo.addons.portal.controllers import portal

from odoo import http
from odoo.http import request
import json

class ResourceCalendarAttendanceAPI(http.Controller):

    @http.route('/api/HiAli', type='http', auth='public', methods=['GET'], csrf=False)
    def hi_ali_api(self ,  **kw):
        cal_type=1
        day='2024-10-28'
        day_number=0

        get_slots = self.get_resource_calendar_attendance_slot(cal_type=cal_type, day=day,day_number =day_number)

        print('Get Sloooots >>>> ' , get_slots)

        return get_slots

    @http.route('/api/resource_calendar_attendance_types', type='http', auth='public', methods=['GET'], csrf=False)
    def get_types(self ,  **kw):
        booking_type = request.env['resource.booking.type'].sudo().search([])
        result=[]
        for i in booking_type:
            result.append({
                'id' : i.id,
                'name' : i.name
            })

        return json.dumps(result)

    @http.route('/api/resource_calendar_attendance_days', type='http', auth='public', methods=['GET'], csrf=False)
    def get_resource_calendar_attendance1(self ,cal_type=None,  **kw):
        if cal_type:
            cal_type = int(cal_type)

            booking_type = request.env['resource.booking.type'].sudo().search([('id', '=', cal_type)])
            if booking_type:
                attendances = booking_type.resource_calendar_id.attendance_ids
                # Filter attendances to include only records where day_period is not 'lunch'
                filtered_attendances = attendances.filtered(lambda att: att.day_period != 'lunch')

                x = filtered_attendances.mapped('dayofweek')

        today = datetime.now().date()

        # Get the start date (today) and end date (today + 7 days)
        end_date = today + timedelta(days=7)

        # Initialize response list
        response = []

        # Iterate through the days from today to the end date
        current_date = today+ timedelta(days=1)
        while current_date <= end_date:
            print('current_date.weekday()' , current_date.weekday())
            # Check if the current day is a working day (you can customize this based on your logic)
            if current_date.weekday() < 7  :  # Assuming Monday to Friday are working days
                response.append({
                    'id': current_date.strftime('%Y-%m-%d'),
                    'title': current_date.strftime('%Y-%m-%d'),
                    'valid' : True if  str(current_date.weekday()) in x else False
                })

            # Move to the next day
            current_date += timedelta(days=1)

        return json.dumps(response)

    @http.route('/api/resource_calendar_attendance', type='http', auth='public', methods=['GET'], csrf=False)
    def get_resource_calendar_attendance(self, calendar_id=None, **kw):
        if not calendar_id:
            return json.dumps({'error': 'Missing calendar_id parameter'})

        # Query ResourceCalendarAttendance records for the given calendar_id where day_period is not 'lunch'
        attendances = request.env['resource.calendar.attendance'].sudo().search([
            ('calendar_id', '=', int(calendar_id)),
            ('day_period', '!=', 'lunch')
        ])

        # Prepare a response dictionary to store day names and available slots
        response = {}

        for attendance in attendances:
            day_name = dict(attendance._fields['dayofweek'].selection).get(attendance.dayofweek)
            time_slots = []

            # Divide the time slot into smaller intervals of 30 minutes
            current_time = attendance.hour_from
            while current_time < attendance.hour_to:
                hours = int(current_time)
                minutes = int((current_time - hours) * 60)
                time_slots.append({
                    'hour_from': f"{hours:02d}:{minutes:02d}",
                    'hour_to': f"{int(current_time+0.5):02d}:{int(((current_time+0.5) % 1) * 60):02d}"
                })
                current_time += 0.5

            if day_name not in response:
                response[day_name] = time_slots
            else:
                response[day_name].extend(time_slots)

        return json.dumps(response)

    # @http.route('/api_/resource_calendar_attendance_slot', type='http', auth='public', methods=['GET'], csrf=False)
    def get_resource_calendar_attendance_slot(self, cal_type=None, day=None, day_number=None):

        if not cal_type or not day:
            return json.dumps({'error': 'Missing cal_type or day parameter'})

        booking_type = request.env['resource.booking.type'].sudo().search([('id', '=', cal_type)])
        if not booking_type:
            return json.dumps({'error': 'Booking type not found'})

        attendances = booking_type.resource_calendar_id.attendance_ids
        day_number = str(day_number)

        # Filter attendances for the given day number and exclude lunch period
        filtered_attendances = attendances.filtered(
            lambda att: str(att.dayofweek) == str(day_number) and att.day_period != 'lunch'
        )

        response = {
            'day_slots': []
        }
        for attendance in filtered_attendances:
            time_slots = []
            current_time = attendance.hour_from

            while current_time < attendance.hour_to:
                hours = int(current_time)
                minutes = int((current_time - hours) * 60)

                # Check for existing bookings before adding the time slot
                existing_booking = request.env['resource.booking'].sudo().search([
                    ('start', '>=', f"{day} {hours:02d}:{minutes:02d}:00"),
                    ('stop', '<=', f"{day} {int(current_time + 0.5):02d}:{int(((current_time + 0.5) % 1) * 60):02d}:00"),
                    ('type_id', '=', int(cal_type)),
                ])

                if not existing_booking:  # No existing booking, add the time slot
                    time_slots.append({
                        'hour_from': f"{hours:02d}:{minutes:02d}",
                        'hour_to': f"{int(current_time + 0.5):02d}:{int(((current_time + 0.5) % 1) * 60):02d}"
                    })

                current_time += 0.5

            response['day_slots'].extend(time_slots)

        return json.dumps(response)




class CustomerPortal(portal.CustomerPortal):
    def _get_booking_sudo(self, booking_id, access_token):
        """Get sudoed booking record from its ID."""
        booking_sudo = self._document_check_access(
            "resource.booking", booking_id, access_token
        )
        return booking_sudo.with_context(
            using_portal=True, tz=booking_sudo.type_id.resource_calendar_id.tz
        )

    def _prepare_home_portal_values(self, counters):
        """Compute values for multi-booking portal views."""
        values = super()._prepare_home_portal_values(counters)
        if "booking_count" in counters:
            booking_count = request.env["resource.booking"].search_count([])
            values.update({"booking_count": booking_count})
        return values

    def _booking_get_page_view_values(self, booking_sudo, access_token, **kwargs):
        """Compute values for single-booking portal views."""
        return self._get_page_view_values(
            booking_sudo,
            access_token,
            {"page_name": "booking", "booking_sudo": booking_sudo},
            "my_bookings_history",
            False,
            **kwargs
        )

    @route(
        ["/my/bookings", "/my/bookings/page/<int:page>"],
        auth="user",
        type="http",
        website=True,
    )
    def portal_my_bookings(self, page=1, **kwargs):
        """List bookings that I can access."""
        Booking = request.env["resource.booking"].with_context(using_portal=True)
        values = self._prepare_portal_layout_values()
        booking_count = Booking.search_count([])
        pager = portal.pager(
            url="/my/bookings",
            total=booking_count,
            page=page,
            step=self._items_per_page,
        )
        bookings = Booking.search(
            [], limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_bookings_history"] = bookings.ids
        values.update({"bookings": bookings, "pager": pager, "page_name": "bookings"})
        return request.render("resource_booking.portal_my_bookings", values)

    @route(["/my/bookings/<int:booking_id>"], type="http", auth="public", website=True)
    def portal_booking_page(self, booking_id, access_token=None, **kwargs):
        """Portal booking form."""
        try:
            booking_sudo = self._get_booking_sudo(booking_id, access_token)
        except (AccessError, MissingError):
            return request.redirect("/my")
        # ensure attachment are accessible with access token inside template
        for attachment in booking_sudo.mapped("message_ids.attachment_ids"):
            attachment.generate_access_token()
        values = self._booking_get_page_view_values(
            booking_sudo, access_token, **kwargs
        )
        return request.render("resource_booking.resource_booking_portal_form", values)

    @route(
        [
            "/my/bookings/<int:booking_id>/schedule",
            "/my/bookings/<int:booking_id>/schedule/<int:year>/<int:month>",
        ],
        auth="public",
        type="http",
        website=True,
    )
    def portal_booking_schedule(
        self, booking_id, access_token=None, year=None, month=None, error=None, **kwargs
    ):
        """Portal booking scheduling."""
        try:
            booking_sudo = self._get_booking_sudo(booking_id, access_token)
        except (AccessError, MissingError):
            return request.redirect("/my")
        values = self._booking_get_page_view_values(
            booking_sudo, access_token, **kwargs
        )
        values.update(booking_sudo._get_calendar_context(year, month))
        values.update({"error": error, "page_name": "booking_schedule"})
        return request.render(
            "resource_booking.resource_booking_portal_schedule", values
        )

    @route(
        ["/my/bookings/<int:booking_id>/cancel"],
        auth="public",
        type="http",
        website=True,
    )
    def portal_booking_cancel(self, booking_id, access_token=None, **kwargs):
        """Cancel the booking."""
        booking_sudo = self._get_booking_sudo(booking_id, access_token)
        booking_sudo.action_cancel()
        return request.redirect("/my")

    @route(
        ["/my/bookings/<int:booking_id>/confirm"],
        auth="public",
        type="http",
        website=True,
    )
    def portal_booking_confirm(self, booking_id, access_token, when, **kwargs):
        """Confirm a booking in a given datetime."""
        booking_sudo = self._get_booking_sudo(booking_id, access_token)
        when_tz_aware = isoparse(when)
        when_naive = datetime.utcfromtimestamp(when_tz_aware.timestamp())
        try:
            with Form(booking_sudo) as booking_form:
                booking_form.start = when_naive
        except ValidationError as error:
            url = booking_sudo.get_portal_url(
                suffix="/schedule/{:%Y/%m}".format(when_tz_aware),
                query_string="&error={}".format(error.args[0]),
            )
            return request.redirect(url)
        booking_sudo.action_confirm()
        return request.redirect(booking_sudo.get_portal_url())
