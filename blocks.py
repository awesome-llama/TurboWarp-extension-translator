
"""File containing all the blocks"""
import re

# https://github.com/scratchfoundation/scratch-parser/blob/d48cf549388f2c0fb7f330e8942c7b299ef4f9a9/lib/sb3_definitions.json
# https://github.com/scratchfoundation/scratch-vm/blob/7419b10eb766574c84b9f33a422614b5eb1fd877/src/serialization/sb3.js#L62
"""
'none': [1, None], # ??
'substack': [2, None], # substack and boolean are separate because the block handling is different
'boolean': [2, None],
'number': [4, '0'],
'positive_number': [5, '0'], # time
'positive_integer': [6, ''], # count
'layer': [7, ''], # layers
'list_item': [7, ''],
'direction': [8, '90'], # set dir
'color': [9, '#000000'],
'text': [10, ''],
'broadcast': [11, None],
'variable_reporter': [12, None],
'list_reporter': [13, None],
"""


class Input():
    def __init__(self):
        pass
    
    def to_list(self):
        # this is the common format used so is default
        if self.block_id is None: return [1, [self.enum, self.value]]
        return [3, self.block_id, [self.enum, self.value]]

    @classmethod
    def from_list(cls, data):
        if data[0] == 1:
            return cls(data[1][1])
        elif data[0] == 2:
            return cls(data[1])
        elif data[0] == 3:
            return cls(data[2][1], data[1])

class InputStack(Input):
    def __init__(self, block_id=None):
        """e.g. if block nesting"""
        self.block_id = block_id
        self.enum = 2
    
    def to_list(self):
        return [self.enum, self.block_id]

class InputBoolean(Input):
    def __init__(self, block_id=None):
        """e.g. not block"""
        self.block_id = block_id
        self.enum = 2
    
    def to_list(self):
        return [self.enum, self.block_id]

class InputNumber(Input):
    def __init__(self, value='', block_id=None): # 4 is any number
        """e.g. math operator"""
        self.value = value
        self.block_id = block_id
        self.enum = 4


class InputPositiveNumber(Input):
    def __init__(self, value='', block_id=None): 
        """e.g. seconds, (oddly) not size"""
        self.value = value
        self.block_id = block_id
        self.enum = 5

class InputPositiveInteger(Input):
    def __init__(self, value='', block_id=None): 
        """e.g. repeat count"""
        self.value = value
        self.block_id = block_id
        self.enum = 6

class InputInteger(Input):
    def __init__(self, value='', block_id=None): 
        """e.g. layer, (oddly) list item but not letter number"""
        self.value = value
        self.block_id = block_id
        self.enum = 7

class InputAngle(Input):
    def __init__(self, value='', block_id=None): 
        """e.g. direction"""
        self.value = value
        self.block_id = block_id
        self.enum = 8

class InputColor(Input):
    def __init__(self, value='#000000', block_id=None): 
        self.value = str(value)
        self.block_id = block_id
        self.enum = 9
    
    def to_list(self):
        if re.fullmatch(r"^#[a-fA-F0-9]{6}$", self.value) is None:
            raise Exception('Not a correctly formatted color')
        return super().to_list()

class InputText(Input):
    def __init__(self, value='', block_id=None): 
        """e.g. say block"""
        self.value = str(value)
        self.block_id = block_id
        self.enum = 10

class InputBroadcast(Input):
    def __init__(self, value='', block_id=None): 
        self.value = str(value)
        self.block_id = block_id
        self.enum = 11

# if block is actually a variable reporter, it should instead be a list [12, var name, var id]
# list reporter is 13
# but this can be ignored and treated as another block id



class Block():
    """Base block class"""
    def __init__(self):
        # self.shape = None # custom val for operator/stack?
        self.opcode = None
        self.next = None
        self.parent = None
        self.raw_inputs = {} # stores inputs as is to be converted later
        self.inputs = {}
        self.fields = {}
        self.shadow = False
        #self.topLevel = False # depends on parent
        self.x = 0
        self.y = 0
        # mutators?
        #self.additional_blocks = [] # this is for dropdowns and other special blocks, used only by some. They should be block objects too.
        # to_dict ignores them 

    def copy_parent(self, source_dict):
        """Copy parent data of a block in dict format"""
        self.parent = source_dict['parent']
        self.x = source_dict.get('x', 0)
        self.y = source_dict.get('y', 0)

    def copy_next(self, source_dict):
        """Copy next data of a block in dict format"""
        self.next = source_dict['next']


    def add_input(self, input_type, key, value):
        """Add an input to the block"""
        if not isinstance(value, input_type):
            raise Exception('input is not of the correct class')
        if key in self.inputs:
            raise Exception('key already exists')
        # the check happens at to_list for block handling
        self.inputs[key] = value.to_list()

    def add_field(self, input_type, key, value):
        # fields don't accept blocks
        raise NotImplementedError

    def to_dict(self):
        # block id is handled outside of this method
        output = {
            "opcode": self.opcode,
            "next": self.next,
            "parent": self.parent,
            "inputs": self.inputs,
            "fields": self.fields,
            "shadow": self.shadow,
            "topLevel": self.parent is None
        }

        if self.parent is None:
            output['x'] = self.x
            output['y'] = self.y

        return output

class OperatorAdd(Block):
    def __init__(self, a:InputNumber, b:InputNumber):
        super().__init__()
        self.opcode = 'operator_add'
        self.add_input(InputNumber, 'NUM1', a)
        self.add_input(InputNumber, 'NUM2', b)

class OperatorSubtract(Block):
    def __init__(self, a:InputNumber, b:InputNumber):
        super().__init__()
        self.opcode = 'operator_subtract'
        self.add_input(InputNumber, 'NUM1', a)
        self.add_input(InputNumber, 'NUM2', b)

class OperatorNot(Block):
    def __init__(self, a:InputBoolean):
        super().__init__()
        self.opcode = 'operator_not'
        self.add_input(InputBoolean, 'OPERAND', a)

class OperatorLessThan(Block):
    def __init__(self, a:InputText, b:InputText):
        super().__init__()
        self.opcode = 'operator_lt'
        self.add_input(InputText, 'OPERAND1', a)
        self.add_input(InputText, 'OPERAND2', b)

class OperatorGreaterThan(Block):
    def __init__(self, a:InputText, b:InputText):
        super().__init__()
        self.opcode = 'operator_gt'
        self.add_input(InputText, 'OPERAND1', a)
        self.add_input(InputText, 'OPERAND2', b)