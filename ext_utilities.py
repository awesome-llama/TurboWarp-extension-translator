import utilities as utils
from blocks import *


def translate_block(project_data, target_index, block_id):
    """Translate a single block"""
    target = project_data['targets'][target_index]
    block = target['blocks'][block_id]
    inputs = block['inputs']

    def replace_and_insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.replace_and_insert_blocks(target, new_blocks, block_id)
    
    match block['opcode']:
        case 'utilities_trueBlock':
            replace_and_insert_helper(OperatorNot(InputBoolean()))
        
        case 'utilities_falseBlock':
            utils.remove_constant_block(target, block_id, 0)
            
        case 'utilities_isLessOrEqual':
            replace_and_insert_helper(OperatorNot(InputBoolean(block=OperatorGreaterThan(
                    InputText.from_list(inputs['A']), 
                    InputText.from_list(inputs['B']),
                    )
                )))
        
        case 'utilities_isMoreOrEqual':
            replace_and_insert_helper(OperatorNot(InputBoolean(block=OperatorLessThan(
                    InputText.from_list(inputs['A']), 
                    InputText.from_list(inputs['B']),
                    )
                )))

        case 'utilities_exponent':
            replace_and_insert_helper(OperatorMathOp(
                'e ^',
                InputNumber(block=OperatorMultiply(
                    InputNumber(block=OperatorMathOp(
                        'ln',
                        InputNumber.from_list(inputs['A']),
                    )),
                    InputNumber.from_list(inputs['B']),
                ))
            ))

        case 'utilities_pi':
            utils.remove_constant_block(target, block_id, 3.141592653589793)

        case 'utilities_currentMillisecond':
            replace_and_insert_helper(OperatorMod(
                    InputNumber(block=OperatorRound(
                        InputNumber(block=OperatorMultiply(
                            InputNumber(block=SensingDaysSince2000()),
                            InputNumber(86400000)
                        ))
                    )),
                    InputNumber(1000),
                ))

        case 'utilities_newline':
            utils.remove_constant_block(target, block_id, '\n')

        case _:
            print(f'opcode not converted: {block['opcode']}')



