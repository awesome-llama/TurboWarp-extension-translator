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


def translate_block(project_data, target_index, block_id):
    """Translate a single block"""
    target = project_data['targets'][target_index]
    block = target['blocks'][block_id]
    inputs = block['inputs']

    def replace_and_insert_helper(new_blocks):
        """Insert a block using current scoped variables"""
        utils.replace_and_insert_blocks(target, new_blocks, block_id)
    
    def _new_comment_stack():
        """Create a comment custom block"""
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

    def _delete_comment_children(input):
        """Blocks can be inserted into the comment text input (of inline comments that will be deleted). They should be deleted too."""
        input_comment = parse_list(input)
        if input_comment.block is not None:
            utils.delete_children(target, input_comment.block)

    match block['opcode']:
        case 'lmscomments_commentHat':
            # hat becomes stack block
            comment_block = _new_comment_stack()
            replace_and_insert_helper(comment_block)

        case 'lmscomments_commentCommand':
            # stack remains as stack
            comment_block = _new_comment_stack()
            replace_and_insert_helper(comment_block)

        case 'lmscomments_commentC':
            # C block becomes if block
            # note that cap blocks prevent this and there is no easy way to check for this
            input_block_id = utils.random_id('new_')
            
            utils.replace_and_insert_blocks(target, OperatorNot(InputBoolean()), input_block_id)

            new_inputs = {'CONDITION': InputBoolean(block=input_block_id).to_list()}
            
            if 'SUBSTACK' in inputs: # copy substack if it exists
                new_inputs['SUBSTACK'] = inputs['SUBSTACK']
            
            _delete_comment_children(inputs['COMMENT'])

            block['opcode'] = 'control_if'
            block['inputs'] = new_inputs


        case 'lmscomments_commentReporter':
            # delete the block
            _delete_comment_children(inputs['COMMENT'])
            input = parse_list(inputs['INPUT'])
            utils.remove_passthrough_block(target, block_id, input.block)
            pass
        
        case 'lmscomments_commentBoolean':
            # delete the block
            _delete_comment_children(inputs['COMMENT'])
            input = parse_list(inputs.get('INPUT', None))
            utils.remove_passthrough_block(target, block_id, input.block)
            pass

        case _:
            print(f'opcode not converted: {block['opcode']}')


