import utilities as utils
from blocks import *

# https://github.com/TurboWarp/extensions/blob/e4f51517be435cd92a0108eb206876a2fe100890/extensions/NOname-awa/graphics2d.js

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
    
    def _direction(dx:Input, dy:Input):
        # Scratch bearings calculation
        return OperatorAdd(
                InputNumber(block=OperatorMathOp(
                    'atan',
                    InputNumber(
                        block=OperatorDivide(
                            InputNumber(block=OperatorSubtract(
                                dx,
                                InputNumber(block=MotionXPosition()),
                            )),
                            InputNumber(block=OperatorSubtract(
                                dy,
                                InputNumber(block=MotionYPosition()),
                            )),
                        )
                    ),
                )),
                InputNumber(block=OperatorMultiply(
                    InputNumber(180),
                    InputNumber(block=OperatorLessThan(
                        InputText.from_object(dy),
                        InputText(block=MotionYPosition())
                    ))
                )),
            )

    match block['opcode']:
        case 'nonameawagraph_line_section':
            # Math.sqrt(Math.pow(args.x1 - args.x2, 2) + Math.pow(args.y1 - args.y2, 2));
            insert_helper(_dist())

        case 'nonameawagraph_ray_direction2':
            # what's wrong with nonameawagraph_ray_direction?
            insert_helper(_direction(
                InputNumber(block=OperatorSubtract(
                    InputNumber.from_list(inputs['x2']),
                    InputNumber.from_list(inputs['x1']),
                )),
                InputNumber(block=OperatorSubtract(
                    InputNumber.from_list(inputs['y2']),
                    InputNumber.from_list(inputs['y1']),
                )),
            ))

        case 'nonameawagraph_vertical':
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

        case 'nonameawagraph_pi':
            utils.remove_constant_block(target, block_id, 3.141592653589793)

        case _:
            print(f'opcode not converted: {block['opcode']}')



