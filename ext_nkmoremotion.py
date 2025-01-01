import utilities as utils
from blocks import *


def translate_block(project_data, target_index, block_id):
    """Translate a single block"""
    target = project_data['targets'][target_index]
    block = target['blocks'][block_id]
    inputs = block['inputs']

    def insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.insert_blocks(target, new_blocks, block_id)
    
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
        case 'nkmoremotion_changexy':
            new_blocks = MotionGoToXY(
                    InputNumber(block=OperatorAdd(
                        InputNumber(block=MotionXPosition()),
                        InputNumber.from_list(inputs['X']),
                    )),
                    InputNumber(block=OperatorAdd(
                        InputNumber(block=MotionYPosition()),
                        InputNumber.from_list(inputs['Y']),
                    )),
                )
            new_blocks.copy_next(block)
            insert_helper(new_blocks)
        
        case 'nkmoremotion_fence':
            new_blocks = MotionChangeXBy(InputNumber(0))
            new_blocks.copy_next(block)
            insert_helper(new_blocks)
        
        case 'nkmoremotion_directionto':
            insert_helper(_direction(InputNumber.from_list(inputs['X']), InputNumber.from_list(inputs['Y'])))
            

        case 'nkmoremotion_pointto':
            new_blocks = MotionPointInDirection(
                InputAngle(block=_direction(InputNumber.from_list(inputs['X']), InputNumber.from_list(inputs['Y'])))
            )
            new_blocks.copy_next(block)
            insert_helper(new_blocks)

        case 'nkmoremotion_distanceto':
            insert_helper(OperatorMathOp(
                'sqrt',
                InputNumber(block=OperatorAdd(
                    InputNumber(block=OperatorMultiply(
                        InputNumber(block=OperatorSubtract(
                            InputNumber.from_list(inputs['X']),
                            InputNumber(block=MotionXPosition()),
                        )),
                        InputNumber(block=OperatorSubtract(
                            InputNumber.from_list(inputs['X']),
                            InputNumber(block=MotionXPosition()),
                        )),
                    )),
                    InputNumber(block=OperatorMultiply(
                        InputNumber(block=OperatorSubtract(
                            InputNumber.from_list(inputs['Y']),
                            InputNumber(block=MotionYPosition()),
                        )),
                        InputNumber(block=OperatorSubtract(
                            InputNumber.from_list(inputs['Y']),
                            InputNumber(block=MotionYPosition()),
                        )),
                    )),
                )),
            ))

        case _:
            print(f'opcode not converted: {block['opcode']}')


