from user.models import UserRoleModel
from inventory.models import InventoryModel


def layout_variable(request):
    if request.user.is_authenticated:
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            user = UserRoleModel.objects.filter(user=user_id)[0]
            if user.id:
                user = user.staff
            else:
                user = ''

            low_stock_list = []
            inventory_list = InventoryModel.objects.all()
            for inventory in inventory_list:
                if inventory.low_level:
                    if inventory.low_level >= inventory.quantity_left:
                        low_stock_list.append(inventory)
            no_of_low_stock = len(low_stock_list)
        else:
            user = '',
            low_stock_list = '',
            no_of_low_stock = 0
    else:
        user = ''
        low_stock_list = ''
        no_of_low_stock = 0

    return {'layout_user': user,
            'low_stock_list': low_stock_list,
            'no_of_low_stock': no_of_low_stock}


