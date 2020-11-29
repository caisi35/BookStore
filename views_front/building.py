from flask import (
    Blueprint, render_template
)

bp = Blueprint('building', __name__)


@bp.route('/building', methods=("GET", ))
def building():
    return render_template('building_404/building.html')