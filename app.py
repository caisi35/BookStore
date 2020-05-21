from flask import Flask
from views_front import user, products, userinfo
from views_admin import admin, signIn, userAdmin, bookAdmin


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # 注册user蓝图，用于登录、注册、注销、账户管理等
    app.register_blueprint(user.bp)

    app.register_blueprint(products.bp)

    app.register_blueprint(userinfo.bp)

    app.register_blueprint(admin.bp)

    app.register_blueprint(signIn.bp)

    app.register_blueprint(userAdmin.bp)

    app.register_blueprint(bookAdmin.bp)

    app.add_url_rule('/', endpoint='index')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
