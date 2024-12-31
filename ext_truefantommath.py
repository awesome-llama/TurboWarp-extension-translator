import utilities as utils
from blocks import *
import math

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
            # reversed intervals allowed
            # max is always used as max even if min is larger
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

        case 'truefantommath_trunc_block':
            # not functionally identical, does not work for infinity
            insert_helper(OperatorMultiply(
                InputNumber(block=OperatorMathOp(
                    'floor',
                    InputNumber(block=OperatorMathOp(
                        'abs',
                        InputNumber.from_list(inputs['A']),
                    )),
                )),
                InputNumber(block=OperatorDivide(
                    InputNumber.from_list(inputs['A']),
                    InputNumber(block=OperatorMathOp(
                        'abs',
                        InputNumber.from_list(inputs['A']),
                    )),
                ))
            ))
        
        case 'truefantommath_trunc2_block':
            # not functionally identical, does not work for infinity
            # also does not work when negative given

            # check if input decimal places is a block or not
            input_dp = InputNumber.from_list(inputs['B'])
            if input_dp.block is None:
                # no block, hard code it
                scale_fac = 10**math.floor(max(0, float(input_dp.shadow_value)))
                input_dp = InputNumber(scale_fac)
            
            insert_helper(OperatorDivide(
                InputNumber(block=OperatorMultiply(
                    InputNumber(block=OperatorMathOp(
                        'floor',
                        InputNumber(block=OperatorMathOp(
                            'abs',
                            InputNumber(block=OperatorMultiply(
                                InputNumber.from_list(inputs['A']),
                                input_dp,
                            ))
                        )),
                    )),
                    InputNumber(block=OperatorDivide(
                        InputNumber.from_list(inputs['A']),
                        InputNumber(block=OperatorMathOp(
                            'abs',
                            InputNumber.from_list(inputs['A']),
                        )),
                )))),
                input_dp,
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
            insert_helper(OperatorNot(InputBoolean(block=OperatorGreaterThan(
                InputText(block=OperatorMathOp(
                    'abs',
                    InputNumber.from_list(inputs['A']),
                )),
                InputText('9007199254740991')
            ))))
        
        case _:
            print(f'opcode not converted: {block['opcode']}')



