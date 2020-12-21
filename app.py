from flask import Flask, render_template
from views_front import user, products, userinfo, building, index_view
from views_admin import admin, signIn, userAdmin, bookAdmin, order_admin


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    # 自定义404错误页面
    app.register_error_handler(404, page_not_found)
    # 注册user蓝图，用于登录、注册、注销、账户管理等
    app.register_blueprint(user.bp)

    app.register_blueprint(products.bp)

    app.register_blueprint(userinfo.bp)

    app.register_blueprint(building.bp)  # 网站建设中页面

    app.register_blueprint(admin.bp)

    app.register_blueprint(signIn.bp)

    app.register_blueprint(userAdmin.bp)

    app.register_blueprint(bookAdmin.bp)

    app.register_blueprint(order_admin.bp)

    app.register_blueprint(index_view.bp)

    app.add_url_rule('/', endpoint='index')

    return app


def page_not_found(e):
    return render_template('building_404/404.htm'), 404


if __name__ == '__main__':
    app = create_app()
    app.run()
