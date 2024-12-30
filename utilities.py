import random
import blocks

def random_id(prefix='', avoid=None):
    """Generate a random id."""
    
    if not isinstance(avoid, (dict, set, list)): avoid = {}

    for _ in range(100):
        temp = str(prefix) + "".join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
        if temp not in avoid:
            return temp
    raise Exception('no vacant ids')



def insert_blocks(target:dict, root_block:blocks.Block, root_block_id:str):
    """Insert multiple blocks into a target. Accepts a root block with inputs containing blocks rather than block_ids."""
    
    def _insert(target, block, block_id):
        """Recursively insert blocks into a target dict. Insert nested blocks first."""
        
        for input_key in list(block.inputs.keys()):
            _block = block.inputs[input_key].block
            if isinstance(_block, blocks.Block):
                # update parent of inner block
                _block.parent = block_id

                _block_id = random_id('new_')
                _insert(target, _block, _block_id) # recurse nested blocks first

                # replace block object with id
                block.inputs[input_key].block = _block_id

                if isinstance(block.inputs[input_key], blocks.InputStack):
                    pass
                    # is a stack block, set the current block next
                    # WIP, check that this is needed
                    # which input is used as next?
            
        # current block now has block ids in its inputs, safe to convert to dict
        target['blocks'][block_id] = block.to_dict()

    ####
    # copy parent data from original unreplaced block
    root_block.copy_parent(target['blocks'][root_block_id])

    # recursively insert
    _insert(target, root_block, root_block_id)



def remove_constant_block(target:dict, block_id:str, value):
    """Remove a block that functioned as a constant and leave behind a literal value"""
    # note this depends on input type. 
    # all bools are left empty because there's no alternative?
    # number and text get stringified value UNLESS the default is actually a shadow block, in that case we do need to add a new block.

    # requires searching all inputs of the parent to find the block

    parent_block_id = target['blocks'][block_id]['parent']
    target['blocks'].pop(block_id) # delete block

    if parent_block_id is None: 
        return # the block does not nest

    for input in target['blocks'][parent_block_id]['inputs'].values():
        if input[0] == 2:
            if input[1] == block_id:
                # don't do anything, no block is needed? unless it's a bool
                pass
        elif input[0] == 3:
            if input[1] == block_id:
                if isinstance(input[2], list):
                    input[2][1] = str(value)
                else:
                    # shadow block
                    raise NotImplementedError()

    



def search_child_blocks(target:dict, root_block_id:str, search_for:str, max_results=None):
    """Search both inputs and next stack block for id"""

    def _search(target, block_id, search_for, max_results, results):
        if target['blocks'][block_id]['opcode'] == search_for:
            results.append(block_id)
        if len(results) >= max_results:
            return # do not search further, enough results found

        # next
        next = target['blocks'][block_id]['next']
        if next is not None:
            _search(target, next, search_for, max_results, results)
    
        # inputs
        for input in target['blocks'][block_id]['inputs'].values():
            if input[0] == 2:
                _search(target, input[1], search_for, max_results, results)
            elif input[0] == 3:
                _search(target, input[1], search_for, max_results, results)

    if max_results is None: max_results = float('inf')
    results = []
    _search(target, root_block_id, search_for, max_results, results)
    return results


def get_procedure_definition_prototype_id(target:dict, definition_id:str):
    # this assumes custom_block key is [1, id]
    return target['blocks'][definition_id]['inputs']['custom_block'][1]
    

