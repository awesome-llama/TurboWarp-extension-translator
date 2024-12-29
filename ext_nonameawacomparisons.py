import utilities as utils
from blocks import *


def translate_block(target, block_id):
    """Translate a single block"""

    block = target['blocks'][block_id]
    inputs = block['inputs']

    def insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.insert_blocks(target, new_blocks, block_id)
    
    match block['opcode']:
        case 'nonameawacomparisons_true':
            insert_helper(OperatorNot(InputBoolean()))
        
        case 'nonameawacomparisons_false':
            # TODO delete the block. if input is not a boolean, replace it with a false value.
            if block['topLevel']:
                target['blocks'].pop(block_id) # top level can be deleted safely

        case _:
            print(f'opcode not converted: {block['opcode']}')



