import utilities as utils
from blocks import *

# https://github.com/TurboWarp/extensions/blob/c791aef076785b7b6fcb98c7880c26bef368775d/extensions/true-fantom/couplers.js

def translate_block(project_data, target_index, block_id):
    """Translate a single block"""
    target = project_data['targets'][target_index]
    block = target['blocks'][block_id]
    inputs = block['inputs']

    def replace_and_insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.replace_and_insert_blocks(target, new_blocks, block_id)
    
    def _remove_passthrough_leave_input(input: Input):
        if input.has_inserted_block(): 
            utils.remove_passthrough_block(target, block_id, input.block)
        
        else: # if None, the value is a literal
            parent_block_id = target['blocks'][block_id]['parent']
            if parent_block_id is None: 
                target['blocks'].pop(block_id)
                return
            
            inputs = target['blocks'][parent_block_id]['inputs']
            for input_id in list(inputs.keys()):
                parsed_input = parse_list(inputs[input_id])
                if parsed_input.block == block_id:
                    inputs[input_id] = input.to_list()

            target['blocks'].pop(block_id)

    match block['opcode']:
        case 'truefantomcouplers_boolean_block':
            # find the value of the shadow
            
            input1 = InputReporter.from_list(inputs['MENU'])
            if input1.block is not None:
                print('truefantomcouplers_boolean_block: cannot remove necessary cast') 
                # scratch doesn't provide an easy way to cast
                # either a list is needed or 2 custom blocks with a swapped parameter
                return

            truefalse_menu_block = target['blocks'][input1.shadow_value]
            truefalse = truefalse_menu_block['fields']['boolean_menu'][0]

            utils.delete_children(target, input1.shadow_value)
            
            if truefalse == 'true':
                replace_and_insert_helper(OperatorNot(InputBoolean()))
            elif truefalse == 'false':
                utils.remove_constant_block(target, block_id, 0)
            elif truefalse == 'random':
                replace_and_insert_helper(OperatorLessThan(
                    InputText(block=OperatorRandom(InputNumber('0'),InputNumber('1.0'))),
                    InputText('0.5')
                    ))
            else:
                print('truefantomcouplers_boolean_block: unknown value')
        
        case 'truefantomcouplers_menu_boolean_menu':
            pass # shadow block, gets removed by parent
        
        case 'truefantomcouplers_value_in_boolean_block':
            # string to bool, not supported
            print('truefantomcouplers_value_in_boolean_block: not supported')

        case 'truefantomcouplers_value_in_string_block':
            # to string
            replace_and_insert_helper(OperatorJoin(InputText.from_list(inputs['VALUE']), InputText('')))

        case 'truefantomcouplers_color_block':
            # the block has no function, it just passes through a colour input.
            input = parse_list(inputs['COLOUR'])
            _remove_passthrough_leave_input(input)

        case 'truefantomcouplers_angle_block':
            input = parse_list(inputs['ANGLE'])
            _remove_passthrough_leave_input(input)

        case 'truefantomcouplers_matrix_block':
            input = parse_list(inputs['MATRIX'])
            
            if input.has_inserted_block():
                utils.remove_passthrough_block(target, block_id, input.block)
            elif input.has_shadow_block():
                utils.remove_passthrough_block(target, block_id, input.shadow_value)
                target['blocks'][input.shadow_value]['shadow'] = False
            else:
                pass
        
        case 'truefantomcouplers_note_block':
            input = parse_list(inputs['NOTE'])
            
            if input.has_inserted_block():
                utils.remove_passthrough_block(target, block_id, input.block)
            elif input.has_shadow_block():
                _remove_passthrough_leave_input(input)
            else:
                pass

        case _:
            print(f'opcode not converted: {block['opcode']}')

