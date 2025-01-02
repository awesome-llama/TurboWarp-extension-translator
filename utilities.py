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



def replace_and_insert_blocks(target:dict, root_block:blocks.Block, root_block_id:str):
    """Insert multiple blocks into a target with the first root block replacing the original (if it exists). Accepts a root block (that may be a stack block or reporter) with inputs containing nested reporter block objects."""

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
    # copy parent and next data from original unreplaced block (if it exists).
    # this is because this block is a direct replacement of existing.
    # nested blocks are always created new and do not have an original block to copy from.
    if root_block_id in target['blocks']:
        root_block.copy_parent(target['blocks'][root_block_id])
        root_block.copy_next(target['blocks'][root_block_id])

    # recursively insert
    _insert(root_block, root_block_id)



def make_not_topLevel(block:dict):
    """Set `topLevel` to false and delete x and y coordinates if they exist"""
    if isinstance(block, list):
        kept_inputs = block[:3] # 12, name, id
        block.clear()
        block.extend(kept_inputs)
    else:
        block['topLevel'] = False
        block.pop('x', None)
        block.pop('y', None)



def connect_stack_blocks(target, block_id_parent, block_id_current, block_id_next):
    """Set next and parent of 2 blocks. Parent and next are allowed to be `None`."""
    if block_id_parent is not None:
        target['blocks'][block_id_parent]['next'] = block_id_current
        make_not_topLevel(target['blocks'][block_id_current])
    
    target['blocks'][block_id_current]['parent'] = block_id_parent
    target['blocks'][block_id_current]['next'] = block_id_next
    
    if block_id_next is not None:
        target['blocks'][block_id_next]['parent'] = block_id_current



def remove_constant_block(target:dict, block_id:str, value):
    """Remove a block that functioned as a constant and leave behind a literal value (which may be inside a join or add if required). It is expected that this constant block has no inputs/children."""
    
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
                replace_and_insert_blocks(target, blocks.OperatorAdd(blocks.InputNumber(value),blocks.InputNumber(0)), input_block_id)
            else:
                replace_and_insert_blocks(target, blocks.OperatorJoin(blocks.InputText(value),blocks.InputText('')), input_block_id)
            target['blocks'][input_block_id]['parent'] = parent_block_id
            make_not_topLevel(target['blocks'][input_block_id])
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
    
    parent_block_id = target['blocks'][block_id]['parent']
    
    if parent_block_id is None: # there was no parent block, assign child as new parent
        if isinstance(child_block_id, list): # var or list reporter
            block = target['blocks'][block_id]
            target['blocks'][block_id] = child_block_id + [block['x'], block['y']]
            return
        elif child_block_id is not None:
            target['blocks'][child_block_id]['parent'] = None
            target['blocks'][child_block_id]['topLevel'] = target['blocks'][block_id]['topLevel']
            target['blocks'][child_block_id]['x'] = target['blocks'][block_id]['x']
            target['blocks'][child_block_id]['y'] = target['blocks'][block_id]['y']
        target['blocks'].pop(block_id)
        return 
    
    if parent_block_id not in target['blocks']:
        parent_block_id = None # if the parent block doesn't exist, set to None rather than id
    else:
        parent_block = target['blocks'][parent_block_id]
        
        for input_key in parent_block['inputs'].keys():
            parsed_input = blocks.parse_list(parent_block['inputs'][input_key])
            if parsed_input.block == block_id:
                parsed_input.block = child_block_id
            parent_block['inputs'][input_key] = parsed_input.to_list()
    
    if child_block_id is not None:
        if not isinstance(child_block_id, list): # ensure it's not a variable or list reporter (which has no parent key)
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
        if isinstance(block_id, list):
            return # block is a variable or list reporter

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
    


def get_all_variables(project_data):
    variables = []
    for target in project_data:
        if 'variables' in target:
            for item in target['variables'].items():
                variables.append(item)
    return variables



def create_variable(project_data, variable_name, variable_value=0, variable_id=None, sprite=None):
    """Create a variable if it does not exist. Error if the variable can not be created due to other existing variables. `sprite=None` means create a global variable (internally stored in the stage)."""

    if variable_id is None: variable_id = random_id('var_')

    # check if the id exists
    # if it does, check for duplicate names, if there are raise exception unless the name and ids match, otherwise do nothing.
    # otherwise check for duplicate names, raise exception if the name exists in stage if local or in any sprite if global.
    # create var.

    def _id_exists():
        for target in project_data['targets']:
            for var_id in target['variables'].keys():
                if var_id == variable_id:
                    return True
        return False

    if _id_exists(): return
    # TODO check for duplicate names

    if sprite is None:
        for target in project_data['targets']:
            if target['isStage']:
                target['variables'][variable_id] = [variable_name, variable_value] # add variable to stage
                return
        raise Exception('no stage found')
    else:
        for target in project_data['targets']:
            if target['name'] == sprite:
                target['variables'][variable_id] = [variable_name, variable_value] # add variable to stage
                return
        raise Exception('no sprite of requested name found')
    

    