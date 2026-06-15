from flask import jsonify


def register_jwt_handlers(jwt):
    @jwt.unauthorized_loader
    def handle_missing_token(reason):
        return jsonify({
            "error": "Authorization token is required",
            "details": reason
        }), 401

    @jwt.invalid_token_loader
    def handle_invalid_token(reason):
        return jsonify({
            "error": "Invalid authorization token",
            "details": reason
        }), 422

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return jsonify({
            "error": "Authorization token has expired"
        }), 401

    @jwt.revoked_token_loader
    def handle_revoked_token(jwt_header, jwt_payload):
        return jsonify({
            "error": "Authorization token has been revoked"
        }), 401

    @jwt.needs_fresh_token_loader
    def handle_fresh_token_required(jwt_header, jwt_payload):
        return jsonify({
            "error": "A fresh authorization token is required"
        }), 401

    @jwt.user_lookup_error_loader
    def handle_user_lookup_error(jwt_header, jwt_payload):
        return jsonify({
            "error": "The user associated with this token was not found"
        }), 401