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
    
    match block['opcode']:
        case 'lmsutilsblocks_whenBooleanHat':
            # replace with timer > bool/-0
            replace_and_insert_helper(EventWhenGreaterThan(
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
                # the key option is now in an if block under the hat
                replace_and_insert_helper(EventWhenKeyPressed('any'))
                new_block_id = utils.random_id('new_')
                new_blocks = ControlIf(
                    InputBoolean(block=SensingKeyPressed(InputReporter(SensingKeyOptions(str(key_option.shadow_value)), block=key_option.block))),
                    InputStack(block=block['next'])
                )
                utils.replace_and_insert_blocks(target, new_blocks, new_block_id)
                utils.connect_stack_blocks(target, block_id, new_block_id, None)
            else:
                replace_and_insert_helper(EventWhenKeyPressed(str(key_option.shadow_value)))

        case 'lmsutilsblocks_keyStringPressed':
            # key press boolean reporter

            key_option = InputText.from_list(inputs['KEY_OPTION'])
            replace_and_insert_helper(SensingKeyPressed(InputReporter(SensingKeyOptions(str(key_option.shadow_value)), block=key_option.block)))
        
        case 'lmsutilsblocks_trueFalseBoolean':
            # find the value of the shadow
            
            input1 = InputReporter.from_list(inputs['TRUEFALSE'])
            if input1.block is not None:
                print('lmsutilsblocks_trueFalseBoolean: cannot remove necessary cast') 
                # scratch doesn't provide an easy way to cast
                # either a list is needed or 2 custom blocks with a swapped parameter
                return

            truefalse_menu_block = target['blocks'][input1.shadow_value]
            truefalse = truefalse_menu_block['fields']['trueFalseMenu'][0]

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
                print('lmsutilsblocks_trueFalseBoolean: unknown value')
        
        case 'lmsutilsblocks_menu_trueFalseMenu':
            pass # shadow block, gets removed by parent

        case 'lmsutilsblocks_norBoolean':
            replace_and_insert_helper(OperatorNot(InputBoolean(block=OperatorOr(
                InputBoolean.from_list(inputs.get('INPUTA', None)),
                InputBoolean.from_list(inputs.get('INPUTB', None)),
            ))))
        
        case 'lmsutilsblocks_xorBoolean':
            replace_and_insert_helper(OperatorNot(InputBoolean(block=OperatorEquals(
                InputText.from_list(inputs.get('INPUTA', None)),
                InputText.from_list(inputs.get('INPUTB', None)),
            ))))
        
        case 'lmsutilsblocks_xnorBoolean':
            replace_and_insert_helper(OperatorEquals(
                InputText.from_list(inputs.get('INPUTA', None)),
                InputText.from_list(inputs.get('INPUTB', None)),
            ))
        
        case 'lmsutilsblocks_nandBoolean':
            replace_and_insert_helper(OperatorNot(InputBoolean(block=OperatorAnd(
                InputBoolean.from_list(inputs.get('INPUTA', None)),
                InputBoolean.from_list(inputs.get('INPUTB', None)),
            ))))

        case 'lmsutilsblocks_notEqualTo':
            replace_and_insert_helper(OperatorNot(InputBoolean(block=OperatorEquals(
                    InputText.from_list(inputs['INPUTA']), 
                    InputText.from_list(inputs['INPUTB']),
                    )
                )))
        
        case 'lmsutilsblocks_moreThanEqual':
            replace_and_insert_helper(OperatorNot(InputBoolean(block=OperatorLessThan(
                    InputText.from_list(inputs['INPUTA']), 
                    InputText.from_list(inputs['INPUTB']),
                    )
                )))

        case 'lmsutilsblocks_lessThanEqual':
            replace_and_insert_helper(OperatorNot(InputBoolean(block=OperatorGreaterThan(
                    InputText.from_list(inputs['INPUTA']), 
                    InputText.from_list(inputs['INPUTB']),
                    )
                )))
        
        case 'lmsutilsblocks_negativeReporter':
            replace_and_insert_helper(
                OperatorSubtract(
                    InputNumber('0'), 
                    InputNumber.from_list(inputs['INPUT'])
                ))
        
        case 'lmsutilsblocks_exponentBlock':
            replace_and_insert_helper(OperatorMathOp(
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
            replace_and_insert_helper(OperatorMathOp(
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
                replace_and_insert_helper(OperatorAdd(
                    InputNumber(block=sign_script),
                    InputNumber(0),
                ))
            else:
                replace_and_insert_helper(sign_script)

        case 'lmsutilsblocks_clampNumber':
            # TODO
            print('lmsutilsblocks_clampNumber: WIP')

        case _:
            print(f'opcode not converted: {block['opcode']}')


