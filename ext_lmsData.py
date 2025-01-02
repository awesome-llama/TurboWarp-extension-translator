import utilities as utils
from blocks import *

# https://github.com/TurboWarp/extensions/blob/292032fcfdbe914dc58a00712f42ab1fc4ac04ca/extensions/Lily/lmsutils.js

def translate_block(project_data, target_index, block_id):
    """Translate a single block"""
    target = project_data['targets'][target_index]
    block = target['blocks'][block_id]
    inputs = block['inputs']

    def replace_and_insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.replace_and_insert_blocks(target, new_blocks, block_id)
    

    def lookup_list_from_name(list_name):
        """Returns 3-tuple of list id, list name, and list contents"""

        # search stage
        for list_id, list_data in utils.get_target(project_data)['lists'].items():
            if list_data[0] == list_name:
                return (list_id, list_data[0], list_data[1])
        
        # search current target
        for list_id, list_data in project_data['targets'][target_index]['lists'].items():
            if list_data[0] == list_name:
                return (list_id, list_data[0], list_data[1])

        
        return None


    match block['opcode']:
        case 'lmsData_listIsEmpty':
            input_base = parse_list(inputs['LIST'])
            if input_base.has_inserted_block():
                print('lmsData_listIsEmpty: reporter input unsupported, list must be chosen before runtime')
                return
            
            menu_block = target['blocks'][input_base.shadow_value]
            chosen_list_name = menu_block['fields']['lists'][0] # the second value is null unfortunately

            chosen_list = lookup_list_from_name(chosen_list_name)
            if chosen_list is None: 
                print('lmsData_listIsEmpty: list name not found')
                return

            utils.delete_children(target, input_base.shadow_value)
            
            replace_and_insert_helper(OperatorEquals(
                InputText(block=DataLengthOfList(chosen_list[1], chosen_list[0])),
                InputText('0'),
            ))
        
        case 'lmsData_menu_lists':
            pass # shadow block

        # note that the for loops use the temp vars extension

        case _:
            print(f'opcode not converted: {block['opcode']}')


