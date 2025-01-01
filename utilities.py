import random
import blocks

random.seed(0)

def random_id(prefix='', avoid=None):
    """Generate a random id."""
    
    if not isinstance(avoid, (dict, set, list)): avoid = {}

    for _ in range(100):
        temp = str(prefix) + "".join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))
        if temp not in avoid:
            return temp
    raise Exception('no vacant ids')



def insert_blocks(target:dict, root_block:blocks.Block, root_block_id:str):
    """Insert multiple blocks into a target. Accepts a root block with inputs containing blocks rather than block_ids."""
    
    def _insert(block, block_id):
        """Recursively insert blocks into a target dict. Insert nested blocks first."""
        
        for input_key in list(block.inputs.keys()):
            # value (may be a shadow block)
            _value = block.inputs[input_key].shadow_value
            if isinstance(_value, blocks.Block):
                # update parent of inner block
                _value.parent = block_id

                _value_id = random_id('new_')
                _insert(_value, _value_id) # recurse nested blocks first

                # replace block object with id
                block.inputs[input_key].shadow_value = _value_id

            # block manually inserted into input
            _block = block.inputs[input_key].block
            if isinstance(_block, blocks.Block):
                # update parent of inner block
                _block.parent = block_id

                _block_id = random_id('new_')
                _insert(_block, _block_id) # recurse nested blocks first

                # replace block object with id
                block.inputs[input_key].block = _block_id
            
        # current block now has block ids in its inputs, safe to convert to dict
        target['blocks'][block_id] = block.to_dict()

    ####
    # copy parent data from original unreplaced block (if it exists)
    if root_block_id in target['blocks']:
        root_block.copy_parent(target['blocks'][root_block_id])

    # recursively insert
    _insert(root_block, root_block_id)



def remove_constant_block(target:dict, block_id:str, value):
    """Remove a block that functioned as a constant and leave behind a literal value. It is expected that this constant block has no inputs."""
    # note this depends on input type. 
    # all bools are left empty because there's no alternative? also note that shadow blocks exist, these should be left
    # requires searching all inputs of the parent to find the block
    
    parent_block_id = target['blocks'][block_id]['parent']

    if parent_block_id is None: 
        target['blocks'].pop(block_id) # delete block
        return # the block does not nest

    parent_block = target['blocks'][parent_block_id]
    for input_key in list(parent_block['inputs'].keys()):
        input = parent_block['inputs'][input_key]
        parsed_input = blocks.parse_list(input)

        if parsed_input.block != block_id: continue # not an input containing the block to remove

        def _insert():
            input_block_id = random_id('new_')
            if isinstance(value, (int, float)):
                # numbers use add block rather than join
                insert_blocks(target, blocks.OperatorAdd(blocks.InputNumber(value),blocks.InputNumber(0)), input_block_id)
            else:
                insert_blocks(target, blocks.OperatorJoin(blocks.InputText(value),blocks.InputText('')), input_block_id)
            target['blocks'][input_block_id]['parent'] = parent_block_id
            target['blocks'][input_block_id]['topLevel'] = False
            target['blocks'][input_block_id].pop('x')
            target['blocks'][input_block_id].pop('y')
            parsed_input.block = input_block_id

        parsed_input.block = None # remove reference to block
        if parsed_input.is_completely_empty():
            if value == 0 or value == False:
                pass # empty input is equivalent to false
            else:
                _insert() # insert a block so the value can be placed in it
        elif parsed_input.has_shadow_block():
            _insert() # insert a block even though there is a field
        else:
            parsed_input.shadow_value = value

        parent_block['inputs'][input_key] = parsed_input.to_list()
        target['blocks'].pop(block_id) # delete block



def remove_passthrough_block(target:dict, block_id:str, child_block_id:str):
    """Remove a block that passed through a value, it has 1 input and 1 output of the same type."""
    
    # this code is poor and confusing
    parent_block_id = target['blocks'][block_id]['parent']
    
    if parent_block_id is None:
        if child_block_id is not None:
            target['blocks'][child_block_id]['parent'] = None
        target['blocks'].pop(block_id)
        return # there was no parent block, assign child as new parent
    
    if parent_block_id not in target['blocks']:
        parent_block_id = None

    else:
        parent_block = target['blocks'][parent_block_id]
        
        for input_key in parent_block['inputs'].keys():
            parsed_input = blocks.parse_list(parent_block['inputs'][input_key])
            if parsed_input.block == block_id:
                parsed_input.block = child_block_id
            parent_block['inputs'][input_key] = parsed_input.to_list()
    
    if child_block_id is not None:
        target['blocks'][child_block_id]['parent'] = parent_block_id # update reference to parent
    target['blocks'].pop(block_id) # finally delete the original block



def delete_children(target:dict, root_block_id:str, inputs_only=True):
    """Recurse over a block's inputs and delete child blocks"""

    def _delete_block(block_id):
        # inputs
        for input in target['blocks'][block_id]['inputs'].values():
            parsed_input = blocks.parse_list(input)
            if parsed_input.block is not None:
                _delete_block(parsed_input.block)

        # search next block too
        if not inputs_only:
            next = target['blocks'][block_id]['next']
            if next is not None:
                _delete_block(next)
        
        target['blocks'].pop(block_id) # delete

    parent_block_id = target['blocks'][root_block_id]['parent'] # store this before it's deleted
    next_block_id = target['blocks'][root_block_id]['next']

    _delete_block(root_block_id)

    # if root was a stack block, ensure that its parent points to the block after
    if parent_block_id is not None:
        if next_block_id not in target['blocks']: # check if the next block still exists (not deleted)
            next_block_id = None
        if target['blocks'][parent_block_id]['next'] == root_block_id:
            target['blocks'][parent_block_id]['next'] = next_block_id
        else:
            print('TODO: check the inputs')
            # TODO if the root was an operator, the parent has an input that needs to be updated



def search_child_blocks(target:dict, root_block_id:str, search_for:str, max_results=None, inputs_only=True):
    """Search both inputs and next stack block for id"""

    if max_results is None: max_results = float('inf')
    results = []

    def _search(block_id):
        if target['blocks'][block_id]['opcode'] == search_for:
            results.append(block_id)
        if len(results) >= max_results:
            return # do not search further, enough results found

        # inputs
        for input in target['blocks'][block_id]['inputs'].values():
            parsed_input = blocks.parse_list(input)
            if parsed_input.block is not None:
                _search(parsed_input.block)
        
        # search next block too
        if not inputs_only:
            next = target['blocks'][block_id]['next']
            if next is not None:
                _search(next)
    
    _search(root_block_id)
    return results



def get_procedure_definition_prototype_id(target:dict, definition_id:str):
    # this assumes custom_block key is [1, id]
    return target['blocks'][definition_id]['inputs']['custom_block'][1]
    

