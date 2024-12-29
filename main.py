import zipfile
import json
import random
from blocks import *

# open file, 
# read vars, lists, targets
# the script can run per-target, there is no need to create/delete global vars or lists

PROJECT = 'projects/all_blocks.sb3'
#PROJECT = 'projects/Project lteq.sb3'

project_archive = zipfile.ZipFile(PROJECT, 'r')
project_data = json.loads(project_archive.read('project.json'))

# list of extensions in project
print(project_data['extensions'])


def random_id(prefix='', avoid=None):
    """Generate a random id."""
    
    if not isinstance(avoid, (dict, set, list)): avoid = {}

    for _ in range(10):
        temp = str(prefix) + "".join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
        if temp not in avoid:
            return temp
    raise Exception('no vacant ids')



def insert_blocks(target, root_block, root_block_id):
    """Insert multiple blocks into a target. Accepts a root block with inputs containing blocks rather than block_ids."""
    
    def _insert(target, block, block_id):
        """Recursively insert blocks into a target dict. Insert nested blocks first."""
        
        for input_key in list(block.inputs.keys()):
            _block = block.inputs[input_key].block
            if isinstance(_block, Block):
                # update parent of inner block
                _block.parent = block_id

                _block_id = random_id('new_')
                _insert(target, _block, _block_id) # recurse nested blocks first

                # replace block object with id
                block.inputs[input_key].block = _block_id

                if isinstance(block.inputs[input_key], InputStack):
                    pass
                    # is a stack block, set the current block next
                    # WIP, check that this is needed
                    # which input is used as next?
            
        # current block now has block ids in its inputs, safe to convert to dict
        target[block_id] = block.to_dict()

    ####
    # copy parent data from original unreplaced block
    root_block.copy_parent(target[root_block_id])
    _insert(target, root_block, root_block_id)


    

for target in project_data['targets']:
    # enumerate over blocks of a target, insert replacements
    for block_id in list(target['blocks'].keys()):
        block = target['blocks'][block_id]
        opcode = block['opcode']
        inputs = block['inputs']

        def insert_helper(new_blocks):
            """Insert a block using current scoped variables"""
            insert_blocks(target['blocks'], new_blocks, block_id)
        
        match opcode:
            case 'truefantommath_negative_block':
                
                insert_helper(
                    OperatorSubtract(
                        InputNumber('0'), 
                        InputNumber.from_list(inputs['A'])
                    ))
                
            case 'lmsutilsblocks_negativeReporter':
                insert_helper(
                    OperatorSubtract(
                        InputNumber('0'), 
                        InputNumber.from_list(inputs['INPUT'])
                    ))
            
            case 'utilities_trueBlock' | 'nonameawacomparisons_true':
                insert_helper(OperatorNot(InputBoolean()))
            
            case 'utilities_falseBlock' | 'nonameawacomparisons_false':
                # TODO delete the block. if input is not a boolean, replace it with a false value.
                if block['topLevel']:
                    target['blocks'].pop(block_id) # top level can be deleted safely
                
            case 'utilities_isLessOrEqual':
                insert_helper(
                    OperatorNot(InputBoolean(
                    OperatorGreaterThan(
                        InputText.from_list(inputs['A']), 
                        InputText.from_list(inputs['B'])
                        )
                    )))
            
            case 'utilities_isMoreOrEqual':
                insert_helper(
                    OperatorNot(InputBoolean(
                    OperatorLessThan(
                        InputText.from_list(inputs['A']), 
                        InputText.from_list(inputs['B'])
                        )
                    )))

            case 'utilities_exponent':
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

            case 'utilities_currentMillisecond':
                insert_helper(
                    OperatorMod(
                        InputNumber(block=OperatorRound(
                            InputNumber(block=OperatorMultiply(
                                InputNumber(block=SensingDaysSince2000()),
                                InputNumber('86400000')
                            ))
                        )),
                        InputNumber('1000')
                    ))









"""
"COLOR": [1, [9, "#12d082"]],
"SIZE": [3, ")", [4, "1"]]
"VALUE": [3, "*", [10, "0"]] # set variable to
"VALUE": [3, "t", [6, "10"]], # for each
"SUBSTACK": [2, "b"] # for each
"STRING": [3, ",", [10, ""]] # 
"COSTUME": [3, "u", "-"] # costume dropdown as shadow
"INDEX": [3, "w", [7, "1"]] # list item index

"NUM1": [3, "/", [4, ""]],
"NUM2": [1, [4, "5"]]
"""


with open('dump.sb3', 'w', encoding='utf-8') as f:
    f.write(json.dumps(project_data, ensure_ascii=False, indent=1))
