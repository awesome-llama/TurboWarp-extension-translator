import utilities as utils
from blocks import *

# https://github.com/TurboWarp/extensions/blob/e4f51517be435cd92a0108eb206876a2fe100890/extensions/Lily/CommentBlocks.js


"""
"+p": {
    "opcode": "procedures_call",
    "next": "aJv",
    "parent": "gJ",
    "inputs": {
        "kn|[@,mw3O_N*d9oAB9C": [1, [10, "COMMENT GOES HERE"]]
    },
    "fields": {},
    "shadow": false,
    "topLevel": false,
    "mutation": {
        "tagName": "mutation",
        "children": [],
        "proccode": "// %s",
        "argumentids": "[\"kn|[@,mw3O_N*d9oAB9C\"]",
        "warp": "false"
    }
},"""


def translate_block(target, block_id):
    """Translate a single block"""

    block = target['blocks'][block_id]
    inputs = block['inputs']

    def insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.insert_blocks(target, new_blocks, block_id)
    
    def _new_comment_stack():
        comment_block = ProceduresCall()
        comment_block.mutation={
            "tagName": "mutation",
            "children": [],
            "proccode": "// %s",
            "argumentids": "[\"lmscomments_comment_param\"]",
            "warp": "false"
        }
        comment_block.add_input(InputText, 'lmscomments_comment_param', InputText.from_list(inputs['COMMENT']))
        comment_block.copy_next(block)
        return comment_block

    match block['opcode']:
        case 'lmscomments_commentHat':
            # hat becomes stack block
            comment_block = _new_comment_stack()
            insert_helper(comment_block)

        case 'lmscomments_commentCommand':
            # stack remains as stack
            comment_block = _new_comment_stack()
            insert_helper(comment_block)

        case 'lmscomments_commentC':
            # C block becomes stack?
            pass

        case 'lmscomments_commentReporter':
            # delete the block
            #input = InputText.from_list(inputs['INPUT'])
            #utils.remove_passthrough_block(target, block_id, input.block)
            pass
        
        case 'lmscomments_commentBoolean':
            # delete the block
            pass

        case _:
            print(f'opcode not converted: {block['opcode']}')


