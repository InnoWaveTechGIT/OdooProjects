from odoo import http, models, _
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.http import Response
import json

class Coupon(http.Controller):

    @http.route('/api/apply_coupon', auth='public', csrf=False, methods=['POST'])
    def apply_coupon(self, **post):
        language = request.httprequest.headers.get('Accept-Language', 'en').split(',')[0]
        try:
            quotation_id = int(post.get('cart_id'))
            coupon_code = post.get('coupon_code')
            # Update the quotation record with the coupon code
            quotation = request.env['sale.order'].sudo().browse(int(quotation_id))

            # Apply the coupon using the SaleLoyaltyCouponWizard
            SaleLoyaltyCouponWizard = request.env['sale.loyalty.coupon.wizard'].sudo().create({
                'order_id': quotation.id,
                'coupon_code': coupon_code
            })
            SaleLoyaltyCouponWizard.action_apply()
            # Apply the reward using the SaleLoyaltyRewardWizard
            SaleLoyaltyRewardWizard = request.env['sale.loyalty.reward.wizard'].sudo().create({
                'order_id': quotation.id,
            })
            reward_ids = SaleLoyaltyRewardWizard.reward_ids.ids

            # Check if any rewards are available to select
            if not reward_ids:
                message = 'الكوبون المدخل غير صالح' if language == 'ar_001' else 'No rewards available'
                response = json.dumps({'message': message})
                return Response(
                    response,
                    status=400,
                    headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
                )

            # Select a reward, assuming you have the reward ID
            selected_reward_id = reward_ids[0]  # Replace this with your logic to select the reward

            # Update the selected reward and apply it
            SaleLoyaltyRewardWizard.write({'selected_reward_id': selected_reward_id})
            SaleLoyaltyRewardWizard.action_apply()
            message = 'تم تطبيق الكوبون' if language == 'ar_001' else 'Coupon and reward applied successfully'
            response = json.dumps({'message': message , 'is_success' :True})
            return Response(
                response,
                status=200,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )
        except ValidationError as e:
            response = json.dumps({'message': str(e) , 'is_success' :False})
            return Response(
                response,
                status=400,
                headers=[('Content-Type', 'application/json'), ('Content-Length', str(len(response)))]
            )