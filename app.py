from flask import Flask
import user
import products


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # 注册user蓝图，用于登录、注册、注销、账户管理等
    app.register_blueprint(user.bp)

    app.register_blueprint(products.bp)
    app.add_url_rule('/', endpoint='index')



    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
