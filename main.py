import zipfile
import json
import utilities as utils
from blocks import *

import ext_lmscomments
import ext_lmsutilsblocks
import ext_nkmoremotion
import ext_nonameawacomparisons
import ext_nonameawagraph
import ext_RixxyX
import ext_truefantommath
import ext_truefantomcouplers
import ext_utilities

# register extensions:
EXTENSIONS = {
    'lmscomments': ext_lmscomments,
    'lmsutilsblocks': ext_lmsutilsblocks,
    'nkmoremotion': ext_nkmoremotion,
    'nonameawacomparisons': ext_nonameawacomparisons,
    'nonameawagraph': ext_nonameawagraph,
    'RixxyX': ext_RixxyX,
    'truefantommath': ext_truefantommath,
    'truefantomcouplers': ext_truefantomcouplers,
    'utilities': ext_utilities,
}

PROJECT = 'projects/all_blocks.sb3'

project_archive = zipfile.ZipFile(PROJECT, 'r')
project_data = json.loads(project_archive.read('project.json'))

# list of extensions in project
print(project_data['extensions'])

# validate variables
# it is assumed ids are always unique, even when the same local var is used in different sprites
variable_ids = set()
for target in project_data['targets']:
    for item in target['variables'].items():
        if item[0] in variable_ids:
            raise Exception('Project variables invalid, same id is used multiple times')
        variable_ids.add(item[0])


for i, target in enumerate(project_data['targets']):

    template_procedures = []

    # enumerate over blocks of a target, insert replacements
    for block_id in list(target['blocks'].keys()):
        if block_id not in target['blocks']: continue # skip deleted blocks

        block = target['blocks'][block_id]

        if isinstance(block, list): continue # variable or list reporter

        opcode = block['opcode']

        opcode_namespace = opcode.split('_')[0] # it seems scratch just calls this id

        if opcode_namespace in ['motion', 'looks', 'sound', 'event', 'control', 'sensing', 'operator', 'data']: 
            continue # these are native blocks
        
        if opcode == 'procedures_definition':
            # count the number of returns, warn if there are too many
            return_blocks = utils.search_child_blocks(target, block_id, 'procedures_return', inputs_only=False)
            if len(return_blocks) > 1:
                print('warning: custom blocks with multiple return statements can not be translated')
                continue
            
            prototype_block = target['blocks'][utils.get_procedure_definition_prototype_id(target, block_id)]

            # mutation is in the prototype
            if prototype_block['mutation']['proccode'][:8] == 'TEMPLATE':
                template_procedures.append(block_id)
            continue
        
        if opcode in ['procedures_definition', 'procedures_prototype', 'procedures_call', 'procedures_return', 'argument_reporter_string_number', 'argument_reporter_string_boolean']:
            continue # custom block

        if opcode_namespace in ['music', 'pen', 'videoSensing', 'translate', 'text2speech', 'makeymakey', 'microbit', 'ev3', 'boost', 'wedo2', 'gdxfor']:
            continue # allowed natively supported extensions
        
        if opcode_namespace in EXTENSIONS:
            EXTENSIONS[opcode_namespace].translate_block(project_data, i, block_id)
        else:
            print(f'namespace unrecognised: {opcode}')

        #raise Exception('unknown opcode')

    # Now replace custom blocks
    print('templates:', template_procedures)
    for block_id in template_procedures:
        #if 'procedures_call'
        pass
        #print(block_id)

with open('dump.sb3', 'w', encoding='utf-8') as f:
    f.write(json.dumps(project_data, ensure_ascii=False, indent=1))
