import utilities as utils
from blocks import *

# https://github.com/TurboWarp/extensions/blob/292032fcfdbe914dc58a00712f42ab1fc4ac04ca/extensions/Lily/lmsutils.js

def translate_block(project_data, target_index, block_id):
    """Translate a single block"""
    target = project_data['targets'][target_index]
    block = target['blocks'][block_id]
    inputs = block['inputs']

    def insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.insert_blocks(target, new_blocks, block_id)
    
    match block['opcode']:
        case 'lmsutilsblocks_whenBooleanHat':
            # replace with timer > bool/-0
            insert_helper(EventWhenGreaterThan(
                'TIMER',
                InputNumber(block=OperatorDivide(
                    InputNumber.from_list(inputs['INPUT']),
                    InputNumber('-0'),
                )),
            ))
        
        case 'lmsutilsblocks_whenKeyString':
            # key press hat
            
            key_option = InputText.from_list(inputs['KEY_OPTION'])

            if key_option.block is not None: 
                print('could not convert lmsutilsblocks_whenKeyString, reporter can not be placed in key option field')
                return
            
            insert_helper(EventWhenKeyPressed(str(key_option.shadow_value)))

        case 'lmsutilsblocks_keyStringPressed':
            # key press boolean reporter

            key_option = InputText.from_list(inputs['KEY_OPTION'])
            
            insert_helper(SensingKeyPressed(InputReporter(SensingKeyOptions(str(key_option.shadow_value)), block=key_option.block)))
        
        case 'lmsutilsblocks_trueFalseBoolean':
            # find the value of the shadow
            
            input1 = InputReporter.from_list(inputs['TRUEFALSE'])
            if input1.block is not None:
                print('cannot remove necessary cast') # TODO: investigate json hacking
                return

            truefalse_menu_block = target['blocks'][input1.shadow_value]
            truefalse = truefalse_menu_block['fields']['trueFalseMenu'][0]

            utils.delete_children(target, input1.shadow_value)
            
            if truefalse == 'true':
                insert_helper(OperatorNot(InputBoolean()))
            elif truefalse == 'false':
                utils.remove_constant_block(target, block_id, 0)
            else:
                pass # random

        case 'lmsutilsblocks_menu_trueFalseMenu':
            pass # shadow block, gets removed by parent

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
            # get the sign of a number. 1 if positive, -1 if negative, 0 otherwise (incl. infinity).
            sign_script = OperatorDivide(
                InputNumber.from_list(inputs['INPUT']),
                InputNumber(block=OperatorMathOp(
                    'abs',
                    InputNumber.from_list(inputs['INPUT']),
                )))

            if True: # note that for parity with extension, add 0 is needed after divide to eliminate NaN
                insert_helper(OperatorAdd(
                    InputNumber(block=sign_script),
                    InputNumber(0),
                ))
            else:
                insert_helper(sign_script)

        case 'lmsutilsblocks_clampNumber':
            # TODO
            print('WIP')

        case _:
            print(f'opcode not converted: {block['opcode']}')


