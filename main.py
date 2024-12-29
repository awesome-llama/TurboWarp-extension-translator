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


# insert block would have to accept the correct inputs for any block and also handle shadow input blocks
def insert_block(target, block, block_id):
    # TODO error handling

    if block_id is None:
        new_id = random_id('new_')
    else: 
        new_id = block_id
    
    target[new_id] = block.to_dict()

    #for additional_block in block.additional_blocks:
    #    insert_block(target, additional_block)
    
#def _insert_from_inputs(target, block)


def insert_blocks(target, root_block, root_block_id):
    """Insert multiple blocks into a target. Accepts a root block with inputs containing blocks rather than block_ids."""
    
    for input_key in root_block['inputs']:
        if isinstance(root_block['inputs'][input_key].block_id, Block):
            pass

    # replace the existing block 
    target[root_block_id] = root_block.to_dict()
    # make sure the inputs and fields don't contain more blocks

    #for additional_block in block.additional_blocks:
    #    insert_block(target, additional_block)
    

for target in project_data['targets']:
    # enumerate over blocks of a target, insert replacements
    for block_id in list(target['blocks'].keys()):
        block = target['blocks'][block_id]
        opcode = block['opcode']
        inputs = block['inputs']
        
        match opcode:
            case 'truefantommath_negative_block':
                b1 = OperatorSubtract(InputNumber('0'), InputNumber.from_list(inputs['A']))
                b1.copy_parent(block)
                insert_block(target['blocks'], b1, block_id)
                
            case 'lmsutilsblocks_negativeReporter':
                b1 = OperatorSubtract(InputNumber('0'), InputNumber.from_list(inputs['INPUT']))
                b1.copy_parent(block)
                insert_block(target['blocks'], b1, block_id)
            
            
            case 'utilities_trueBlock' | 'nonameawacomparisons_true':
                b1 = OperatorNot(InputBoolean())
                b1.copy_parent(block)
                insert_block(target['blocks'], b1, block_id)
            
            case 'utilities_falseBlock' | 'nonameawacomparisons_false':
                # actually is it better to delete the block? depends on the input, right?
                #block['opcode'] = 'operator_and'
                pass
            
            case 'utilities_isLessOrEqual':
                # old working method
                b1_id = random_id('new_')
                b1 = OperatorGreaterThan(InputText.from_list(inputs['A']), InputText.from_list(inputs['B']))
                b1.parent = block_id
                insert_block(target['blocks'], b1, b1_id)

                b2 = OperatorNot(InputBoolean(b1_id))
                b2.copy_parent(block)
                insert_block(target['blocks'], b2, block_id)

                # TODO make this simpler
                # insert block is confusing
                # perhaps nest blocks in input rather than id? too complicated?
                # the input stores a block object and that gets converted later
                # but what about the needed parent?
                # child is solved

                # new idea: construct a tree of ids, these are then just used to correct the parents
                """
                new_blocks = OperatorNot(InputBoolean(
                    OperatorGreaterThan(
                        InputText.from_list(inputs['A']), 
                        InputText.from_list(inputs['B'])
                        )
                    ))
                insert_blocks(target['blocks'], new_blocks, block_id)"""










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
