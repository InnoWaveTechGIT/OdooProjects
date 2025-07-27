from odoo.http import request, route, Controller
import json
from werkzeug.wrappers import Response

class AboutUsController(Controller):

    @route('/about_us', auth="public", csrf=False, website=True, methods=['GET'])
    def about_us(self, **kw):
        # Get the about us record using request.env
        about_us_record = request.env['about.us.haven'].search([], limit=1)

        if not about_us_record:
            return Response(
                json.dumps({"error": "No About Us record found"}),
                status=404,
                headers=[('Content-Type', 'application/json')]
            )

        # Prepare the response data
        response_data = {
            'title': about_us_record.title,
            'brief': about_us_record.brief,
            'facebook': about_us_record.face_book,
            'linkedin': about_us_record.linked_in,
            'instagram': about_us_record.instagram,

        }

        return Response(
            json.dumps({"data": response_data}),
            status=200,
            headers=[('Content-Type', 'application/json')]
        )
