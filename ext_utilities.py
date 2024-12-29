import utilities as utils
from blocks import *


def translate_block(target, block_id):
    """Translate a single block"""

    block = target['blocks'][block_id]
    inputs = block['inputs']

    def insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.insert_blocks(target, new_blocks, block_id)
    
    match block['opcode']:
        case 'utilities_trueBlock':
            insert_helper(OperatorNot(InputBoolean()))
        
        case 'utilities_falseBlock':
            # TODO delete the block. if input is not a boolean, replace it with a false value.
            if block['topLevel']:
                target['blocks'].pop(block_id) # top level can be deleted safely
            
        case 'utilities_isLessOrEqual':
            insert_helper(
                OperatorNot(InputBoolean(
                OperatorGreaterThan(
                    InputText.from_list(inputs['A']), 
                    InputText.from_list(inputs['B'])
                    )
                )))
        
        case 'utilities_isMoreOrEqual':
            insert_helper(
                OperatorNot(InputBoolean(
                OperatorLessThan(
                    InputText.from_list(inputs['A']), 
                    InputText.from_list(inputs['B'])
                    )
                )))

        case 'utilities_exponent':
            insert_helper(OperatorMathOp(
                'e ^',
                InputNumber(block=OperatorMultiply(
                    InputNumber(block=OperatorMathOp(
                        'ln',
                        InputNumber.from_list(inputs['A']),
                    )),
                    InputNumber.from_list(inputs['B']),
                ))
            ))

        case 'utilities_currentMillisecond':
            insert_helper(
                OperatorMod(
                    InputNumber(block=OperatorRound(
                        InputNumber(block=OperatorMultiply(
                            InputNumber(block=SensingDaysSince2000()),
                            InputNumber('86400000')
                        ))
                    )),
                    InputNumber('1000')
                ))

        case _:
            print(f'opcode not converted: {block['opcode']}')



