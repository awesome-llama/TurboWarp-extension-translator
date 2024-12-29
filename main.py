import zipfile
import json
import utilities as utils
from blocks import *

import ext_lmsutilsblocks
import ext_nkmoremotion
import ext_nonameawacomparisons
import ext_truefantommath
import ext_utilities


PROJECT = 'projects/all_blocks.sb3'
#PROJECT = 'projects/Project lteq.sb3'

project_archive = zipfile.ZipFile(PROJECT, 'r')
project_data = json.loads(project_archive.read('project.json'))

# list of extensions in project
print(project_data['extensions'])

for target in project_data['targets']:

    template_procedures = []

    # enumerate over blocks of a target, insert replacements
    for block_id in list(target['blocks'].keys()):
        block = target['blocks'][block_id]
        opcode = block['opcode']

        opcode_namespace = opcode.split('_')[0] # it seems scratch just calls this id

        if opcode_namespace in ['motion', 'looks', 'sound', 'event', 'control', 'sensing', 'operator', 'data']: 
            continue # these are native blocks
        
        if opcode == 'procedures_definition':
            # count the number of returns, warn if there are too many
            return_blocks = utils.search_child_blocks(target, block_id, 'procedures_return')
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
        
        match opcode_namespace:
            case 'lmsutilsblocks':
                ext_lmsutilsblocks.translate_block(target, block_id)

            case 'nkmoremotion':
                ext_nkmoremotion.translate_block(target, block_id)

            case 'nonameawacomparisons':
                ext_nonameawacomparisons.translate_block(target, block_id)

            case 'truefantommath':
                ext_truefantommath.translate_block(target, block_id)

            case 'utilities':
                ext_utilities.translate_block(target, block_id)
            
            case _:
                print(f'namespace unrecognised: {opcode}')

        #raise Exception('unknown opcode')

# Now replace custom blocks
print(template_procedures)
for block_id in template_procedures:
    #if 'procedures_call'
    print(block_id)

with open('dump.sb3', 'w', encoding='utf-8') as f:
    f.write(json.dumps(project_data, ensure_ascii=False, indent=1))
