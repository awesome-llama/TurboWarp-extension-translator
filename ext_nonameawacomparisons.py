import utilities as utils
from blocks import *

# https://github.com/TurboWarp/extensions/blob/292032fcfdbe914dc58a00712f42ab1fc4ac04ca/extensions/NOname-awa/more-comparisons.js

def translate_block(target, block_id):
    """Translate a single block"""

    block = target['blocks'][block_id]
    inputs = block['inputs']

    def insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.insert_blocks(target, new_blocks, block_id)
    
    def _dist(x1='x1', y1='y1', x2='x2', y2='y2'):
        # 2d distance calculation
        return OperatorMathOp(
            'sqrt',
            InputNumber(block=OperatorAdd(
                InputNumber(block=OperatorMultiply(
                    InputNumber(block=OperatorSubtract(
                        InputNumber.from_list(inputs[x2]),
                        InputNumber.from_list(inputs[x1]),
                    )),
                    InputNumber(block=OperatorSubtract(
                        InputNumber.from_list(inputs[x2]),
                        InputNumber.from_list(inputs[x1]),
                    )),
                )),
                InputNumber(block=OperatorMultiply(
                    InputNumber(block=OperatorSubtract(
                        InputNumber.from_list(inputs[y2]),
                        InputNumber.from_list(inputs[y1]),
                    )),
                    InputNumber(block=OperatorSubtract(
                        InputNumber.from_list(inputs[y2]),
                        InputNumber.from_list(inputs[y1]),
                    )),
                )),
            )),
        )
    
    match block['opcode']:
        case 'nonameawacomparisons_true':
            insert_helper(OperatorNot(InputBoolean()))
        
        case 'nonameawacomparisons_false':
            utils.remove_constant_block(target, block_id, 0)

        case 'nonameawacomparisons_boolean':
            print('boolean cast WIP')
            pass

        case 'nonameawacomparisons_booleanToInt':
            # cast to int
            insert_helper(OperatorAdd(InputNumber.from_list(inputs.get('a', None)), InputNumber(0)))
        
        case 'nonameawacomparisons_equalNegative':
            # args.a == 0 - args.b;
            insert_helper(OperatorEquals(
                InputText.from_list(inputs['a']),
                InputText(block=OperatorSubtract(InputNumber(0), InputNumber.from_list(inputs['b']))),
            ))

        case 'nonameawacomparisons_equalPlusMinus':
            # args.a == 0 - args.b || args.a == args.b;
            # why no abs?
            insert_helper(OperatorOr(
                InputBoolean(block=OperatorEquals(
                    InputText.from_list(inputs['a']),
                    InputText.from_list(inputs['b']),
                )),
                InputBoolean(block=OperatorEquals(
                    InputText.from_list(inputs['a']),
                    InputText(block=OperatorSubtract(InputNumber(0), InputNumber.from_list(inputs['b']))),
                )),
            ))

        case 'nonameawacomparisons_notEqual':
            insert_helper(OperatorNot(InputBoolean(block=OperatorEquals(
                InputText.from_list(inputs['a']),
                InputText.from_list(inputs['b']),
            ))))

        case 'nonameawacomparisons_almostEqual2n':
            # Math.round(args.a) == Math.round(args.b);
            insert_helper(OperatorEquals(
                InputText(block=OperatorRound(InputNumber.from_list(inputs['a']))),
                InputText(block=OperatorRound(InputNumber.from_list(inputs['b']))),
            ))

        case 'nonameawacomparisons_almostEqual3n':
            # Math.abs(args.a - args.b) <= args.c;
            insert_helper(OperatorNot(InputBoolean(block=
                OperatorGreaterThan(
                    InputText(block=OperatorMathOp(
                        'abs',
                        InputNumber(block=OperatorSubtract(
                            InputNumber.from_list(inputs['a']),
                            InputNumber.from_list(inputs['b']),
                        )),
                    )),
                    InputText.from_list(inputs['c'])
                )
            )))

        case 'nonameawacomparisons_xor':
            # Scratch.Cast.toBoolean(args.a) !== Scratch.Cast.toBoolean(args.b);
            insert_helper(OperatorNot(InputBoolean(block=OperatorEquals(
                InputText.from_list(inputs.get('a', None)),
                InputText.from_list(inputs.get('b', None)),
            ))))

        case 'nonameawacomparisons_equalOrGreater':
            insert_helper(OperatorNot(InputBoolean(block=OperatorLessThan(
                    InputText.from_list(inputs['a']), 
                    InputText.from_list(inputs['b']),
                    )
                )))

        case 'nonameawacomparisons_equalOrLess':
            insert_helper(OperatorNot(InputBoolean(block=OperatorGreaterThan(
                    InputText.from_list(inputs['a']), 
                    InputText.from_list(inputs['b']),
                    )
                )))
        
        case 'nonameawacomparisons_between':
            # a < b < c
            insert_helper(OperatorAnd(
                InputBoolean(block=OperatorLessThan(
                    InputText.from_list(inputs['a']),
                    InputText.from_list(inputs['b']),
                )),
                InputBoolean(block=OperatorLessThan(
                    InputText.from_list(inputs['b']),
                    InputText.from_list(inputs['c']),
                )),
            ))

        case 'nonameawacomparisons_betweenEqual':
            # a <= b <= c
            insert_helper(OperatorNot(InputBoolean(block=OperatorOr(
                InputBoolean(block=OperatorGreaterThan(
                    InputText.from_list(inputs['a']),
                    InputText.from_list(inputs['b']),
                )),
                InputBoolean(block=OperatorGreaterThan(
                    InputText.from_list(inputs['b']),
                    InputText.from_list(inputs['c']),
                )),
            ))))
        
        case 'nonameawacomparisons_vertical':
            # (args.a - (args.b - 90)) % 180 == 0;
            insert_helper(OperatorEquals(
                InputText(block=OperatorMod(
                    InputNumber(block=OperatorSubtract(
                        InputNumber.from_list(inputs['a']),
                        InputNumber(block=OperatorSubtract(
                            InputNumber.from_list(inputs['b']),
                            InputNumber(90),
                        )),
                    )),
                    InputNumber(180),
                )),
                InputText(0),
            ))

        case 'nonameawacomparisons_segment_one':
            # round(dist) = 
            insert_helper(OperatorEquals(
                InputText(block=OperatorRound(
                    InputNumber(block=_dist())
                )),
                InputText.from_list(inputs['n']),
            ))

        case 'nonameawacomparisons_segment_two':
            insert_helper(OperatorEquals(
                InputText(block=OperatorRound(
                    InputNumber(block=_dist('x11', 'y11', 'x12', 'y12'))
                )),
                InputText(block=OperatorRound(
                    InputNumber(block=_dist('x21', 'y21', 'x22', 'y22'))
                )),
            ))

        case 'nonameawacomparisons_segment':
            # Math.sqrt(Math.pow(args.x1 - args.x2, 2) + Math.pow(args.y1 - args.y2, 2));
            insert_helper(_dist())

        case _:
            print(f'opcode not converted: {block['opcode']}')



