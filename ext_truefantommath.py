import utilities as utils
from blocks import *

# https://github.com/TurboWarp/extensions/blob/292032fcfdbe914dc58a00712f42ab1fc4ac04ca/extensions/true-fantom/math.js

def translate_block(target, block_id):
    """Translate a single block"""

    block = target['blocks'][block_id]
    inputs = block['inputs']

    def insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.insert_blocks(target, new_blocks, block_id)
    
    match block['opcode']:
        case 'truefantommath_exponent_block':
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

        case 'truefantommath_root_block':
            insert_helper(OperatorMathOp(
                'e ^',
                InputNumber(block=OperatorDivide(
                    InputNumber(block=OperatorMathOp(
                        'ln',
                        InputNumber.from_list(inputs['A']),
                    )),
                    InputNumber.from_list(inputs['B']),
                ))
            ))

        case 'truefantommath_negative_block':
            insert_helper(OperatorSubtract(
                    InputNumber('0'), 
                    InputNumber.from_list(inputs['A']),
                ))
        
        case 'truefantommath_more_or_equal_block':
            insert_helper(OperatorNot(InputBoolean(block=OperatorLessThan(
                    InputText.from_list(inputs['A']), 
                    InputText.from_list(inputs['B']),
                    )
                )))

        case 'truefantommath_less_or_equal_block':
            insert_helper(OperatorNot(InputBoolean(block=OperatorGreaterThan(
                    InputText.from_list(inputs['A']), 
                    InputText.from_list(inputs['B']),
                    )
                )))
        
        case 'truefantommath_not_equal_block':
            insert_helper(OperatorNot(InputBoolean(block=OperatorEquals(
                    InputText.from_list(inputs['A']), 
                    InputText.from_list(inputs['B']),
                    )
                )))
        
        case 'truefantommath_almost_equal_block':
            insert_helper(OperatorNot(InputBoolean(block=OperatorGreaterThan(
                    InputText(block=OperatorMathOp(
                        'abs',
                        InputNumber(block=OperatorSubtract(
                            InputNumber.from_list(inputs['A']),
                            InputNumber.from_list(inputs['B']),
                        )),
                    )), 
                    InputText(0.5),
                    )
                )))
        
        case 'truefantommath_not_almost_equal_block':
            insert_helper(OperatorGreaterThan(
                    InputText(block=OperatorMathOp(
                        'abs',
                        InputNumber(block=OperatorSubtract(
                            InputNumber.from_list(inputs['A']),
                            InputNumber.from_list(inputs['B']),
                        )),
                    )), 
                    InputText(0.5),
                ))
        
        case 'truefantommath_between_or_equal':
            # a <= b <= c
            insert_helper(OperatorNot(InputBoolean(block=OperatorOr(
                InputBoolean(block=OperatorGreaterThan(
                    InputText.from_list(inputs['A']),
                    InputText.from_list(inputs['B']),
                )),
                InputBoolean(block=OperatorGreaterThan(
                    InputText.from_list(inputs['B']),
                    InputText.from_list(inputs['C']),
                )),
            ))))
        
        case 'truefantommath_between':
            # a < b < c
            insert_helper(OperatorAnd(
                InputBoolean(block=OperatorLessThan(
                    InputText.from_list(inputs['A']),
                    InputText.from_list(inputs['B']),
                )),
                InputBoolean(block=OperatorLessThan(
                    InputText.from_list(inputs['B']),
                    InputText.from_list(inputs['C']),
                )),
            ))

        case 'truefantommath_nand_block':
            # !(cast.toBoolean(A) && cast.toBoolean(B));
            insert_helper(OperatorNot(InputBoolean(block=OperatorAnd(
                InputBoolean.from_list(inputs.get('A', None)),
                InputBoolean.from_list(inputs.get('B', None)),
            ))))

        case 'truefantommath_nor_block':
            # !(cast.toBoolean(A) || cast.toBoolean(B));
            insert_helper(OperatorNot(InputBoolean(block=OperatorOr(
                InputBoolean.from_list(inputs.get('A', None)),
                InputBoolean.from_list(inputs.get('B', None)),
            ))))
        
        case 'truefantommath_xor_block':
            # cast.toBoolean(A) !== cast.toBoolean(B);
            insert_helper(OperatorNot(InputBoolean(block=OperatorEquals(
                InputText.from_list(inputs.get('A', None)),
                InputText.from_list(inputs.get('B', None)),
            ))))

        case 'truefantommath_xnor_block':
            # cast.toBoolean(A) === cast.toBoolean(B);
            insert_helper(OperatorEquals(
                InputText.from_list(inputs.get('A', None)),
                InputText.from_list(inputs.get('B', None)),
            ))

        case 'truefantommath_clamp_block':
            # TODO
            pass
        
        case 'truefantommath_scale_block':
            # map range
            # ((cast.toNumber(A) - cast.toNumber(m1)) * (cast.toNumber(M2) - cast.toNumber(m2))) / (cast.toNumber(M1) - cast.toNumber(m1)) + cast.toNumber(m2)
            insert_helper(OperatorAdd(
                InputNumber(block=OperatorDivide(
                    InputNumber(block=OperatorMultiply(
                        InputNumber(block=OperatorSubtract(
                            InputNumber.from_list(inputs['A']),
                            InputNumber.from_list(inputs['m1']),
                        )),
                        InputNumber(block=OperatorSubtract(
                            InputNumber.from_list(inputs['M2']),
                            InputNumber.from_list(inputs['m2']),
                        )),
                    )),
                    InputNumber(block=OperatorSubtract(
                        InputNumber.from_list(inputs['M1']),
                        InputNumber.from_list(inputs['m1']),
                    )),
                )),
                InputNumber.from_list(inputs['m2']),
            ))

        case 'truefantommath_is_multiple_of_block':
            # cast.toNumber(A) % cast.toNumber(B) === 0;
            insert_helper(OperatorEquals(
                InputText(block=OperatorMod(
                    InputNumber.from_list(inputs['A']),
                    InputNumber.from_list(inputs['B']),
                )),
                InputText(0),
            ))

        case 'truefantommath_log_with_base_block':
            # Math.log(cast.toNumber(A)) / Math.log(cast.toNumber(B));
            insert_helper(OperatorDivide(
                InputNumber(block=OperatorMathOp(
                    'ln',
                    InputNumber.from_list(inputs['A']),
                )),
                InputNumber(block=OperatorMathOp(
                    'ln',
                    InputNumber.from_list(inputs['B']),
                )),
            ))
            pass

        case 'truefantommath_pi_block':
            utils.remove_constant_block(target, block_id, 3.141592653589793)

        case 'truefantommath_e_block':
            utils.remove_constant_block(target, block_id, 2.718281828459045)

        case 'truefantommath_infinity_block':
            utils.remove_constant_block(target, block_id, 'Infinity')

        case 'truefantommath_is_safe_number_block':
            # TODO
            #insert_helper()
            pass
        
        case _:
            print(f'opcode not converted: {block['opcode']}')



