from flask import Flask
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    cache.init_app(app)

    # from .routes import (
    #     json_xml_routes, sql_formatter_routes,
    #     uuid_generator_routes, jwt_decoder_routes,
    #     hash_generator_routes, timestamp_routes,
    #     curl_to_code_routes, diff_tool_routes,
    #     mock_data_routes, color_converter_routes,
    #     base64_routes, url_encoder_routes,
    #     qr_code_routes, lorem_ipsum_routes,
    #     http_status_routes
    # )

    from .routes import (
        json_xml_routes, sql_formatter_routes
    )

    app.register_blueprint(json_xml_routes.bp)
    app.register_blueprint(sql_formatter_routes.bp)
    # Register all other blueprints...

    return app