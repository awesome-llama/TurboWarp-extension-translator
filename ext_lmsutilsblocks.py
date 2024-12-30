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
        case 'lmsutilsblocks_negativeReporter':
            insert_helper(
                OperatorSubtract(
                    InputNumber('0'), 
                    InputNumber.from_list(inputs['INPUT'])
                ))
        
        case _:
            print(f'opcode not converted: {block['opcode']}')


