from odoo.http import request

class CorsHelper:
    
    @staticmethod
    def cors_headers():
        allowed_origins = [
            'http://yhc-app.dtz-internal-only.com'
        ]

        origin = request.httprequest.headers.get('Origin')
        if origin in allowed_origins:
            return [
                ('Access-Control-Allow-Origin', origin),
                ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, X-Unit-Token'),
                ('Access-Control-Allow-Credentials', 'true')
            ]
        return []
