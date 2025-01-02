import utilities as utils
from blocks import *

# https://github.com/TurboWarp/extensions/blob/c791aef076785b7b6fcb98c7880c26bef368775d/extensions/NexusKitten/moremotion.js

STEP_DIST_NAME = 'nkmoremotion_steptowards_ratio'
STEP_DIST_ID = utils.random_id('var_')

def translate_block(project_data, target_index, block_id):
    """Translate a single block"""
    target = project_data['targets'][target_index]
    block = target['blocks'][block_id]
    inputs = block['inputs']

    def replace_and_insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.replace_and_insert_blocks(target, new_blocks, block_id)
    
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
    
    def _dist_from_sprite(x='X', y='Y'):
        """Distance using sprite's position"""
        return OperatorMathOp(
            'sqrt',
            InputNumber(block=OperatorAdd(
                InputNumber(block=OperatorMultiply(
                    InputNumber(block=OperatorSubtract(
                        InputNumber.from_list(inputs[x]),
                        InputNumber(block=MotionXPosition()),
                    )),
                    InputNumber(block=OperatorSubtract(
                        InputNumber.from_list(inputs[x]),
                        InputNumber(block=MotionXPosition()),
                    )),
                )),
                InputNumber(block=OperatorMultiply(
                    InputNumber(block=OperatorSubtract(
                        InputNumber.from_list(inputs[y]),
                        InputNumber(block=MotionYPosition()),
                    )),
                    InputNumber(block=OperatorSubtract(
                        InputNumber.from_list(inputs[y]),
                        InputNumber(block=MotionYPosition()),
                    )),
                )),
            )),
        )

    match block['opcode']:
        case 'nkmoremotion_changexy':
            replace_and_insert_helper(MotionGoToXY(
                    InputNumber(block=OperatorAdd(
                        InputNumber(block=MotionXPosition()),
                        InputNumber.from_list(inputs['X']),
                    )),
                    InputNumber(block=OperatorAdd(
                        InputNumber(block=MotionYPosition()),
                        InputNumber.from_list(inputs['Y']),
                    )),
                ))
        
        case 'nkmoremotion_fence':
            replace_and_insert_helper(MotionChangeXBy(InputNumber(0)))
        
        case 'nkmoremotion_steptowards':
            # it only makes sense to create a variable for this
            utils.create_variable(project_data, STEP_DIST_NAME, 0, STEP_DIST_ID, target['name'])
            replace_and_insert_helper(DataSetVariableTo(STEP_DIST_NAME, STEP_DIST_ID, InputText(block=OperatorDivide(
                InputNumber.from_list(inputs['STEPS']),
                InputNumber(block=_dist_from_sprite()),
            ))))
            
            new_block_id = utils.random_id('new_')
            new_blocks = ControlIfElse(
                InputBoolean(OperatorLessThan(
                    InputText(block=[12, STEP_DIST_NAME, STEP_DIST_ID]),
                    InputText(1),
                )),
                InputStack(block=MotionGoToXY(
                    InputNumber(block=OperatorAdd(
                        InputNumber(block=MotionXPosition()),
                        InputNumber(block=OperatorMultiply(
                            InputNumber(block=[12, STEP_DIST_NAME, STEP_DIST_ID]),
                            InputNumber(block=OperatorSubtract(
                                InputNumber.from_list(inputs['X']),
                                InputNumber(block=MotionXPosition()),
                            )),
                        )),
                    )),
                    InputNumber(block=OperatorAdd(
                        InputNumber(block=MotionYPosition()),
                        InputNumber(block=OperatorMultiply(
                            InputNumber(block=[12, STEP_DIST_NAME, STEP_DIST_ID]),
                            InputNumber(block=OperatorSubtract(
                                InputNumber.from_list(inputs['Y']),
                                InputNumber(block=MotionYPosition()),
                            )),
                        )),
                    )),
                )),
                InputStack(block=MotionGoToXY(
                    InputNumber.from_list(inputs['X']), # too close, go to destination
                    InputNumber.from_list(inputs['Y']),
                )))
            
            utils.replace_and_insert_blocks(target, new_blocks, new_block_id)
            utils.connect_stack_blocks(target, block_id, new_block_id, block['next'])
            

        case 'nkmoremotion_tweentowards':
            # util.target.setXY(
            #    (x - util.target.x) * (val / 100) + util.target.x,
            #    (y - util.target.y) * (val / 100) + util.target.y
            # );
            replace_and_insert_helper(MotionGoToXY(
                InputNumber(block=OperatorAdd(
                    InputNumber(block=OperatorMultiply(
                        InputNumber(block=OperatorSubtract(
                            InputNumber.from_list(inputs['X']),
                            InputNumber(block=MotionXPosition()),
                        )),
                        InputNumber(block=OperatorDivide(
                            InputNumber.from_list(inputs['PERCENT']),
                            InputNumber(100),
                        )),
                    )),
                    InputNumber(block=MotionXPosition()),
                )),
                InputNumber(block=OperatorAdd(
                    InputNumber(block=OperatorMultiply(
                        InputNumber(block=OperatorSubtract(
                            InputNumber.from_list(inputs['Y']),
                            InputNumber(block=MotionYPosition()),
                        )),
                        InputNumber(block=OperatorDivide(
                            InputNumber.from_list(inputs['PERCENT']),
                            InputNumber(100),
                        )),
                    )),
                    InputNumber(block=MotionYPosition()),
                ))))
            

        case 'nkmoremotion_directionto':
            replace_and_insert_helper(_direction(InputNumber.from_list(inputs['X']), InputNumber.from_list(inputs['Y'])))
        
        case 'nkmoremotion_pointto':
            replace_and_insert_helper(MotionPointInDirection(
                InputAngle(block=_direction(InputNumber.from_list(inputs['X']), InputNumber.from_list(inputs['Y'])))
            ))

        case 'nkmoremotion_distanceto':
            replace_and_insert_helper(_dist_from_sprite())

        case _:
            print(f'opcode not converted: {block['opcode']}')


