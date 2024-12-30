import utilities as utils
from blocks import *

# https://github.com/TurboWarp/extensions/blob/292032fcfdbe914dc58a00712f42ab1fc4ac04ca/extensions/Lily/lmsutils.js

def translate_block(target, block_id):
    """Translate a single block"""

    block = target['blocks'][block_id]
    inputs = block['inputs']

    def insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.insert_blocks(target, new_blocks, block_id)
    
    match block['opcode']:
        case 'lmsutilsblocks_whenBooleanHat':
            # replace with timer > bool/-0
            print(inputs['INPUT'])
            insert_helper(EventWhenGreaterThan(
                'TIMER',
                InputNumber(block=OperatorDivide(
                    InputNumber.from_list(inputs['INPUT']),
                    InputNumber('-0'),
                )),
            ))
        
        case 'lmsutilsblocks_whenKeyString':
            # key press hat
            # check if there is an inserted block
            #inputs['INPUT'] # get value, either it's a block or a value
            insert_helper(EventWhenKeyPressed('space'))

        case 'lmsutilsblocks_keyStringPressed':
            # key press boolean
            insert_helper(SensingKeyPressed(InputReporter(
                SensingKeyOptions('space'),
                block=OperatorJoin(
                    InputText.from_list(inputs['KEY_OPTION']),
                    InputText(''),
                )
            )))
        
        case 'lmsutilsblocks_trueFalseBoolean':
            # find the value of the shadow
            #'lmsutilsblocks_menu_trueFalseMenu'
            # insert_helper(OperatorNot(InputBoolean()))
            # utils.remove_constant_block(target, block_id, 0)
            pass

        case 'lmsutilsblocks_menu_trueFalseMenu':
            pass # shadow block, gets removed by parent
        
        case 'lmsutilsblocks_keyStringPressed':
            # key press but accept any input
            pass

        case 'lmsutilsblocks_norBoolean':
            insert_helper(OperatorNot(InputBoolean(block=OperatorOr(
                InputBoolean.from_list(inputs.get('INPUTA', None)),
                InputBoolean.from_list(inputs.get('INPUTB', None)),
            ))))
        
        case 'lmsutilsblocks_xorBoolean':
            insert_helper(OperatorNot(InputBoolean(block=OperatorEquals(
                InputText.from_list(inputs.get('INPUTA', None)),
                InputText.from_list(inputs.get('INPUTB', None)),
            ))))
        
        case 'lmsutilsblocks_xnorBoolean':
            insert_helper(OperatorEquals(
                InputText.from_list(inputs.get('INPUTA', None)),
                InputText.from_list(inputs.get('INPUTB', None)),
            ))
        
        case 'lmsutilsblocks_nandBoolean':
            insert_helper(OperatorNot(InputBoolean(block=OperatorAnd(
                InputBoolean.from_list(inputs.get('INPUTA', None)),
                InputBoolean.from_list(inputs.get('INPUTB', None)),
            ))))

        case 'lmsutilsblocks_notEqualTo':
            insert_helper(OperatorNot(InputBoolean(block=OperatorEquals(
                    InputText.from_list(inputs['INPUTA']), 
                    InputText.from_list(inputs['INPUTB']),
                    )
                )))
        
        case 'lmsutilsblocks_moreThanEqual':
            insert_helper(OperatorNot(InputBoolean(block=OperatorLessThan(
                    InputText.from_list(inputs['INPUTA']), 
                    InputText.from_list(inputs['INPUTB']),
                    )
                )))

        case 'lmsutilsblocks_lessThanEqual':
            insert_helper(OperatorNot(InputBoolean(block=OperatorGreaterThan(
                    InputText.from_list(inputs['INPUTA']), 
                    InputText.from_list(inputs['INPUTB']),
                    )
                )))
        
        case 'lmsutilsblocks_negativeReporter':
            insert_helper(
                OperatorSubtract(
                    InputNumber('0'), 
                    InputNumber.from_list(inputs['INPUT'])
                ))
        
        case 'lmsutilsblocks_exponentBlock':
            insert_helper(OperatorMathOp(
                'e ^',
                InputNumber(block=OperatorMultiply(
                    InputNumber(block=OperatorMathOp(
                        'ln',
                        InputNumber.from_list(inputs['INPUTA']),
                    )),
                    InputNumber.from_list(inputs['INPUTB']),
                ))
            ))

        case 'lmsutilsblocks_rootBlock':
            insert_helper(OperatorMathOp(
                'e ^',
                InputNumber(block=OperatorDivide(
                    InputNumber(block=OperatorMathOp(
                        'ln',
                        InputNumber.from_list(inputs['INPUTA']),
                    )),
                    InputNumber.from_list(inputs['INPUTB']),
                ))
            ))

        case 'lmsutilsblocks_normaliseValue':
            # sign
            # note that for parity with extension, add 0 is needed after divide
            insert_helper(OperatorDivide(
                InputNumber.from_list(inputs['INPUT']),
                InputNumber(block=OperatorMathOp(
                    'abs',
                    InputNumber.from_list(inputs['INPUT']),
                ))
            ))

        case 'lmsutilsblocks_clampNumber':
            # TODO
            print('WIP')

        case _:
            print(f'opcode not converted: {block['opcode']}')


