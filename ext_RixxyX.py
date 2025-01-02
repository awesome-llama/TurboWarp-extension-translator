import utilities as utils
from blocks import *

# https://github.com/TurboWarp/extensions/blob/c791aef076785b7b6fcb98c7880c26bef368775d/extensions/rixxyx.js

COUNTER_NAME = 'RixxyX_counter'
COUNTER_ID = utils.random_id('var_')

def translate_block(project_data, target_index, block_id):
    """Translate a single block"""
    target = project_data['targets'][target_index]
    block = target['blocks'][block_id]
    inputs = block['inputs']

    def replace_and_insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.replace_and_insert_blocks(target, new_blocks, block_id)

    match block['opcode']:
        case 'RixxyX_notEquals':
            replace_and_insert_helper(OperatorNot(InputBoolean(block=OperatorEquals(
                    InputText.from_list(inputs['TEXT_1']), 
                    InputText.from_list(inputs['TEXT_2']),
                    )
                )))

        case 'RixxyX_color':
            # the block has no function, it just passes through a colour input.
            
            input = parse_list(inputs['COLOR'])

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


        case 'RixxyX_returnTrue':
            replace_and_insert_helper(OperatorNot(InputBoolean()))
        
        case 'RixxyX_returnFalse':
            utils.remove_constant_block(target, block_id, 0)

        case 'RixxyX_returnString':
            replace_and_insert_helper(OperatorJoin(InputText.from_list(inputs['TEXT']), InputText('')))

        case 'RixxyX_returnCount':
            if block['topLevel']:
                # replace with variable reporter
                block = [12, COUNTER_NAME, COUNTER_ID, block['x'], block['y']]
            else:
                # look for the parent and insert variable into it
                parent_block = target['blocks'][block['parent']]
                for input_key in list(parent_block['inputs'].keys()):
                    input = parent_block['inputs'][input_key]
                    parsed_input = parse_list(input)
                    if parsed_input.block == block_id:
                        parsed_input.block = [12, COUNTER_NAME, COUNTER_ID]
                        parent_block['inputs'][input_key] = parsed_input.to_list()
                
                target['blocks'].pop(block_id) # delete this block as it's no longer needed
            
        case 'RixxyX_incrementCountByNum':
            utils.create_variable(project_data, COUNTER_NAME, 0, COUNTER_ID)
            replace_and_insert_helper(DataChangeVariableBy(COUNTER_NAME, COUNTER_ID, InputNumber.from_list(inputs['NUM'])))

        case 'RixxyX_decrementCountByNum':
            utils.create_variable(project_data, COUNTER_NAME, 0, COUNTER_ID)
            parsed_input = InputNumber.from_list(inputs['NUM'])
            if parsed_input.block is None: # literal can be used by itself, no subtract block needed
                parsed_input = InputNumber(-float(parsed_input.shadow_value))
                new_blocks = DataChangeVariableBy(COUNTER_NAME, COUNTER_ID, parsed_input)
            else:
                new_blocks = DataChangeVariableBy(COUNTER_NAME, COUNTER_ID, InputNumber(block=OperatorSubtract(InputNumber(0), parsed_input)))
            replace_and_insert_helper(new_blocks)

        case 'RixxyX_setCount':
            utils.create_variable(project_data, COUNTER_NAME, 0, COUNTER_ID)
            replace_and_insert_helper(DataSetVariableTo(COUNTER_NAME, COUNTER_ID, InputText.from_list(inputs['NUM'])))

        case 'RixxyX_isJsNan':
            # functionally identical
            replace_and_insert_helper(OperatorEquals(
                InputText.from_list(inputs['OBJ']),
                InputText('NaN'),
            ))

        case 'RixxyX_returnNum':
            # Math.floor(args.NUM);
            # it unintuitively returns a floored number
            replace_and_insert_helper(OperatorMathOp('floor', InputNumber.from_list(inputs['NUM'])))

        case 'RixxyX_returnBool':
            # TODO cast string to bool
            #input = parse_list(inputs['BOOL'])
            #utils.remove_passthrough_block(target, block_id, input.block)
            pass

        case 'RixxyX_returnENum':
            # e constant
            utils.remove_constant_block(target, block_id, 2.718281828459045)

        case _:
            print(f'opcode not converted: {block['opcode']}')


