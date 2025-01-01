import utilities as utils
from blocks import *

# https://github.com/TurboWarp/extensions/blob/c791aef076785b7b6fcb98c7880c26bef368775d/extensions/rixxyx.js#L25

def translate_block(target, block_id):
    """Translate a single block"""

    block = target['blocks'][block_id]
    inputs = block['inputs']

    def insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.insert_blocks(target, new_blocks, block_id)

    match block['opcode']:
        case 'RixxyX_notEquals':
            insert_helper(OperatorNot(InputBoolean(block=OperatorEquals(
                    InputText.from_list(inputs['TEXT_1']), 
                    InputText.from_list(inputs['TEXT_2']),
                    )
                )))

        case 'RixxyX_color':
            pass

        case 'RixxyX_returnTrue':
            insert_helper(OperatorNot(InputBoolean()))
        
        case 'RixxyX_returnFalse':
            utils.remove_constant_block(target, block_id, 0)

        case 'RixxyX_returnString':
            insert_helper(OperatorJoin(InputText.from_list(inputs['TEXT']), InputText('')))

        # counter goes here
        # create variable RixxyX_counter

        case 'RixxyX_isJsNan':
            # functionally identical
            insert_helper(OperatorEquals(
                InputText.from_list(inputs['OBJ']),
                InputText('NaN'),
            ))

        case 'RixxyX_returnNum':
            # it unintuitively returns a floored number
            # Math.floor(args.NUM);
            insert_helper(OperatorMathOp('floor', InputNumber.from_list(inputs['NUM'])))

        case 'RixxyX_returnBool':
            # TODO cast string to bool
            # 
            pass

        case 'RixxyX_returnENum':
            # e constant
            utils.remove_constant_block(target, block_id, 2.718281828459045)

        case _:
            print(f'opcode not converted: {block['opcode']}')


