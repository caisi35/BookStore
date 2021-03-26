from .user_events_model import (
    user_register_model,
    user_login_model,
    add_visits,
)

from .address_model import (
    get_user_addr_info,
    get_addr_list_model,
    delete_addr_model,
    set_default_addr_model,
    edit_addr_model,
    get_addr_info,
)

from .userinf_model import (
    edit_userinfo_model,
    upload_avatar_model,
    change_pwd_model,
)

from .products_model import (
    index_model,
    get_book,
    get_user,
    add_card_model,
    get_user_cart,
    edit_cart_num,
    from_cart_buy,
    to_buy_model,
    update_addr,
    delete_addr,
    to_pay_model,
    pay_model,
    get_order_info,
    search_book_model,
    get_evaluate,
    get_recommend_book_model,
    get_recommend_user_book_model,
)

from .orders_model import (
    get_user_orders_model,
    user_delete_order,
    get_order_details_model,
    get_badge_model,
    cancel_model,
    refund_model,
    evaluate_model,
    update_status,
    update_status_user_id,
    get_book_id,
)
